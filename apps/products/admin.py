from django.contrib import admin
from .models import Category, Product, Review, ReviewVote


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('-created_at',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount', 'stock', 'is_organic', 'is_flash_sale')
    list_filter = ('category', 'is_organic', 'is_flash_sale')
    search_fields = ('name', 'description')


class ReviewVoteInline(admin.TabularInline):
    model = ReviewVote
    extra = 0

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')
    inlines = [ReviewVoteInline]