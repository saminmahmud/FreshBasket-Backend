from rest_framework import status
from rest_framework.test import APITestCase
from tests.base import BaseTestCase
from apps.products.models import Category, Product, Review, ReviewVote
from apps.orders.models import Order, OrderItem
from decimal import Decimal


class ReviewAPITestCase(BaseTestCase, APITestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Fruits"
        )

        self.product = Product.objects.create(
            name="Apple",
            description="Fresh apple",
            price=100,
            category=self.category,
            unit="kg",
            stock=20,
        )

        self.user = self.create_user(
            username="customer",
            password="password123"
        )

        self.url = (
            f"/api/products/"
            f"{self.product.id}/reviews/"
        )

    def test_list_reviews_is_public(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_create_review_requires_verified_user(self):
        self.user = self.create_user(
            username="unverified",
            password="password123",
            verified=False,
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            data={
                "rating": 5,
                "comment": "Excellent product",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_create_review_requires_delivered_order(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            data={
                "rating": 5,
                "comment": "Excellent product",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "You can only review products you have purchased and received.",
            str(response.data),
        )

    def test_user_can_create_review_after_purchase(self):
        self.client.force_authenticate(
            user=self.user
        )

        order = Order.objects.create(
            user=self.user,
            full_name="Test Customer",
            phone="01700000000",
            address="Test Address",
            latitude=Decimal("23.8103000"),
            longitude=Decimal("90.4125000"),
            city="Dhaka",
            postal_code="1200",
            payment_method="cash_on_delivery",
            order_status="delivered",
            delivery_area="inside_dhaka",
            subtotal=self.product.price,
            delivery_charge=Decimal("60.00"),
        )

        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            price=self.product.price,
        )

        response = self.client.post(
            self.url,
            data={
                "product": self.product.id,
                "rating": 5,
                "comment": "Excellent product",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Review.objects.filter(
                user=self.user,
                product=self.product,
                rating=5,
                comment="Excellent product",
            ).exists()
        )

        
        
        
        
        
        
        
        
