from rest_framework import serializers
from .models import Category, Product, Review, ReviewVote
from apps.users.serializers import UserMiniSerializer


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


class ReviewVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewVote
        fields = ['id', 'review', 'is_helpful']


class ProductListSerializer(serializers.ModelSerializer):
    category = CategoryForProductSerializer(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    total_reviews = serializers.IntegerField(read_only=True)
    final_discount = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'image', 'category', 'price', 'final_price', 'final_discount', 'unit', 'unit_quantity', 'is_flash_sale', 'average_rating', 'total_reviews']


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategoryForProductSerializer(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    total_reviews = serializers.IntegerField(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    final_discount = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'image', 'category', 'price', 'final_price', 'final_discount', 'stock', 'unit', 'unit_quantity', 'is_organic', 'is_flash_sale', 'average_rating', 'total_reviews', 'reviews']