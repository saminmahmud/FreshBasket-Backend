from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import * 

router = DefaultRouter()

router.register('categories', CategoryViewSet, basename='category')
router.register('products', ProductViewSet, basename='product')


urlpatterns = [
    path('products/flash-sales/', FlashSaleProductListAPIView.as_view(), name='flash-sale-product-list'),
    path('products/<int:product_id>/reviews/', ReviewViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-reviews'),
    path('reviews/<int:review_id>/vote/', ReviewVoteAPIView.as_view(), name='review-vote'),
    path("", include(router.urls)),
]