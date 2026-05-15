from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets, filters
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from apps.products.filters import ProductFilter
from apps.users.permissions import IsEmailVerified
from .models import Category, Product, Review, ReviewVote
from rest_framework import permissions
from .serializers import CategorySerializer, ProductDetailSerializer, ProductListSerializer, ReviewSerializer, ReviewCreateSerializer, ReviewVoteSerializer
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        else:
            return [permissions.AllowAny()]


class ReviewViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_id']).select_related('user')

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user, product_id=self.kwargs['product_id'])

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAdminUser()]
        else:
            return [permissions.AllowAny()]
        

class ReviewVoteAPIView(APIView):
    permission_classes = [IsEmailVerified | permissions.IsAdminUser]

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
    queryset = Product.objects.all().select_related('category').prefetch_related('reviews')
    pagination_class = PageNumberPagination
    page_size = 8
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name']
    ordering_fields = ['price', 'created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        else:
            return [permissions.AllowAny()]

