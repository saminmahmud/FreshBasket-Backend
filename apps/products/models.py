from cloudinary_storage.storage import MediaCloudinaryStorage
from django.db import models
from django_resized import ResizedImageField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = ResizedImageField(size=[300, 300], upload_to='categories/', null=True, blank=True, quality=75, storage=MediaCloudinaryStorage())
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['name']),
        ]
        verbose_name_plural = 'Categories'
        verbose_name = 'Category'


class Product(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('l', 'Liter'),
        ('ml', 'Milliliter'),
        ('pcs', 'Pieces'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00) # e.g., 10.00 for 10% discount
    image = ResizedImageField(size=[432, 432], upload_to='products/', null=True, blank=True, quality=75, storage=MediaCloudinaryStorage())
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='kg')
    unit_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1.00) # e.g., 250 for 250g
    stock = models.PositiveIntegerField(default=0)
    is_organic = models.BooleanField(default=False)
    is_flash_sale = models.BooleanField(default=False)
    flash_sale_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00) # e.g., 20.00 for 20% flash sale discount
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'created_at']),
            models.Index(fields=['price']),
            models.Index(fields=['is_organic']),
            models.Index(fields=['is_flash_sale']),
        ]

    @property
    def final_price(self):
        price = self.price
        if self.is_flash_sale and self.flash_sale_discount > 0:
            price = price * (Decimal('1.0') - (self.flash_sale_discount / Decimal('100')))
        elif self.discount > 0:
            price = price * (Decimal('1.0') - (self.discount / Decimal('100')))
        return price  

    @property
    def final_discount(self):
        if self.is_flash_sale and self.flash_sale_discount > 0:
            return self.flash_sale_discount
        elif self.discount > 0:
            return self.discount
        return Decimal('0.00') 

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return None 
    
    @property
    def total_reviews(self):
        return self.reviews.count()
       

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)]) # 1 to 5
    comment = models.TextField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user.username} for {self.product.name}'
    
    class Meta:
        unique_together = ('product', 'user')
        indexes = [
            models.Index(fields=['product']), 
            models.Index(fields=['product', 'rating']),
        ]
        ordering = ['-created_at']

    @property
    def helpful_votes(self):
        return self.votes.filter(is_helpful=True).count()
    

class ReviewVote(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_helpful = models.BooleanField(default=True)

    class Meta:
        unique_together = ('review', 'user')



