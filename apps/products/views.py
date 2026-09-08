from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets, filters, permissions, generics
from rest_framework.views import APIView
from apps.products.custom_pagination import ProductPagination
from apps.products.filters import ProductFilter
from apps.users.permissions import IsEmailVerified
from .models import Category, Product, Review, ReviewVote
from .serializers import CategorySerializer, ProductDetailSerializer, ProductListSerializer, ReviewSerializer, ReviewCreateSerializer, ReviewVoteSerializer
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Avg, Count, Exists, OuterRef, Q, Prefetch
from apps.orders.models import OrderItem


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        else:
            return [permissions.AllowAny()]
        
    @method_decorator(cache_page(60 * 10))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs) 


class ReviewViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Review.objects.none()
        
        queryset = Review.objects.filter(product_id=self.kwargs['product_id']).select_related('user').annotate(
            helpful_votes_count=Count('votes', filter=Q(votes__is_helpful=True), distinct=True)
        )
        
        user = self.request.user
        
        if user.is_authenticated:
            queryset = queryset.prefetch_related(
                Prefetch(
                    'votes',
                    queryset=ReviewVote.objects.filter(
                        user=user,
                        is_helpful=True
                    ),
                    to_attr='current_user_helpful_votes'
                )
            )
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user, product_id=self.kwargs['product_id'])

    def get_permissions(self):
        if self.action in ['create']:
            return [IsEmailVerified()]
        return [permissions.AllowAny()]
        

class ReviewVoteAPIView(APIView):
    permission_classes = [IsEmailVerified | permissions.IsAdminUser]
    serializer_class = None

    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)

        vote, created = ReviewVote.objects.get_or_create(review=review, user=request.user)
        if not created:
            vote.is_helpful = not vote.is_helpful
            vote.save()
            
        total_helpful = ReviewVote.objects.filter(review=review, is_helpful=True).count()

        return Response({
            'review_id': review.id,
            'is_helpful': vote.is_helpful,
            'total_helpful': total_helpful
        })


class ProductViewSet(viewsets.ModelViewSet):
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name']
    ordering_fields = ['price', 'created_at']
    parser_classes = [MultiPartParser, FormParser, JSONParser] 

    def get_queryset(self):
        queryset = Product.objects.select_related('category').annotate(
            average_rating=Avg('reviews__rating'),
            total_reviews=Count('reviews', distinct=True),
        )

        if self.action == 'retrieve':
            user = self.request.user
            
            review_queryset = Review.objects.select_related(
                "user"
            ).annotate(
                helpful_votes_count=Count(
                    "votes",
                    filter=Q(votes__is_helpful=True),
                    distinct=True,
                )
            )

            if user.is_authenticated:
                review_queryset = review_queryset.prefetch_related(
                    Prefetch(
                        "votes",
                        queryset=ReviewVote.objects.filter(
                            user=user,
                            is_helpful=True,
                        ),
                        to_attr="current_user_helpful_votes",
                    )
                )
                
                queryset = queryset.annotate(
                    user_has_review=Exists(
                        Review.objects.filter(
                            product=OuterRef('pk'),
                            user=user
                        )
                    ),
                    user_can_review=Exists(
                        OrderItem.objects.filter(
                            product=OuterRef('pk'),
                            order__user=user,
                            order__order_status='delivered'
                        )
                    ),
                )
            
            queryset = queryset.prefetch_related(
                Prefetch(
                    'reviews',
                    queryset=review_queryset,
                )
            )

        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        else:
            return [permissions.AllowAny()]
        
    @method_decorator(cache_page(60 * 10))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 10))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    
class FlashSaleProductListAPIView(generics.ListAPIView):
    # queryset = Product.objects.filter(is_flash_sale=True).select_related('category').prefetch_related('reviews', 'reviews__user')
    queryset = Product.objects.filter(is_flash_sale=True).select_related('category').annotate(
            average_rating=Avg('reviews__rating'),
            total_reviews=Count('reviews'),
        )
    pagination_class = ProductPagination
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    
    @method_decorator(cache_page(60 * 10))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)