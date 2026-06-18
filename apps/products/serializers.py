from rest_framework import serializers
from .models import Category, Product, Review, ReviewVote
from apps.users.serializers import UserMiniSerializer
from apps.orders.models import OrderItem
from drf_spectacular.utils import extend_schema_field


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image']


class CategoryForProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ReviewSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    helpful_votes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'created_at', 'helpful_votes']


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

    def validate(self, attrs):
        user = self.context['request'].user
        product_id = self.context['view'].kwargs['product_id']

        if Review.objects.filter(user=user, product_id=product_id).exists():
            raise serializers.ValidationError("You have already reviewed this product.")
        
        if not OrderItem.objects.filter(product_id=product_id, order__user=user, order__order_status='delivered').exists():
            raise serializers.ValidationError("You can only review products you have purchased and received.")
        
        return attrs


class ReviewVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewVote
        fields = ['id', 'review', 'is_helpful']


class ProductListSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category" 
    )
    category = CategoryForProductSerializer(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    total_reviews = serializers.IntegerField(read_only=True)
    final_discount = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        allow_null=True
    )
    flash_sale_discount = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'image', 'category', 'price', 'final_price', 'final_discount', 'stock', 'unit', 'unit_quantity', 'is_organic', 'is_flash_sale', 'average_rating', 'total_reviews', 'discount', 'flash_sale_discount', 'category_id']
        


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategoryForProductSerializer(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    total_reviews = serializers.IntegerField(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    final_discount = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_create_review = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'image', 'category', 'price', 'final_price', 'final_discount', 'stock', 'unit', 'unit_quantity', 'is_organic', 'is_flash_sale', 'average_rating', 'total_reviews', 'reviews', 'is_create_review']

    @extend_schema_field(serializers.BooleanField)
    def get_is_create_review(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            if obj.reviews.filter(user=user).exists():
                return False

            return OrderItem.objects.filter(product=obj, order__user=user, order__order_status='delivered').exists()
        return False
