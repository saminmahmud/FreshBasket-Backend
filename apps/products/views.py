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
        return Review.objects.filter(product_id=self.kwargs['product_id']).select_related('user')

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

        return Response({
            'review_id': review.id,
            'is_helpful': vote.is_helpful,
            'total_helpful': review.helpful_votes
        })


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related('category').prefetch_related('reviews', 'reviews__user')
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name']
    ordering_fields = ['price', 'created_at']
    parser_classes = [MultiPartParser, FormParser, JSONParser] 

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
    queryset = Product.objects.filter(is_flash_sale=True).select_related('category').prefetch_related('reviews', 'reviews__user')
    pagination_class = ProductPagination
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    
    method_decorator(cache_page(60 * 10))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)