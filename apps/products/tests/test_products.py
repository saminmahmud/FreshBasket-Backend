from rest_framework import status
from rest_framework.test import APITestCase
from tests.base import BaseTestCase
from apps.products.models import Category, Product
from decimal import Decimal


class ProductsAPITestCase(BaseTestCase, APITestCase):
    def setUp(self):
        self.url = "/api/products/"

        self.category = Category.objects.create(
            name="Fruits"
        )

        self.user = self.create_user(
            username="customer",
            password="password123"
        )

        self.product = Product.objects.create(
            name="Apple",
            description="Fresh apple",
            price=Decimal("100.00"),
            discount=Decimal("10.00"),
            category=self.category,
            unit="kg",
            unit_quantity=Decimal("1.00"),
            stock=20,
            is_organic=True,
        )

    def test_list_products(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_retrieve_product(self):
        response = self.client.get(
            f"{self.url}{self.product.id}/"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Apple")
        self.assertEqual(
            Decimal(response.data["final_price"]),
            Decimal("90.00")
        )
        self.assertEqual(
            Decimal(response.data["final_discount"]),
            Decimal("10.00")
        )
        
    def test_flash_sale_has_priority_over_normal_discount(self):
        self.product.is_flash_sale = True
        self.product.flash_sale_discount = Decimal("20.00")
        self.product.save()

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.final_price,
            Decimal("80.00")
        )

        self.assertEqual(
            self.product.final_discount,
            Decimal("20.00")
        )
        
    def test_create_product_requires_admin(self):
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(
            self.url,
            data={
                "name": "Banana",
                "description": "Fresh banana",
                "price": "80.00",
                "category_id": self.category.id,
                "unit": "kg",
                "unit_quantity": "1.00",
                "stock": 10,
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_create_product_as_admin(self):
        self.user.is_staff = True
        self.user.save()

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            data={
                "name": "Banana",
                "description": "Fresh banana",
                "price": "80.00",
                "category_id": self.category.id,
                "unit": "kg",
                "unit_quantity": "1.00",
                "stock": 10,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertTrue(
            Product.objects.filter(name="Banana").exists()
        )
        
    def test_search_products(self):
        response = self.client.get(
            self.url,
            {"search": "Apple"}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(len(response.data["results"]), 1)
        
    def test_filter_products_by_category(self):
        response = self.client.get(
            self.url,
            {"category": self.category.id}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_ordering_products_by_price(self):
        Product.objects.create(
            name="Banana",
            description="Fresh banana",
            price=Decimal("50.00"),
            category=self.category,
            unit="kg",
            stock=10,
        )
        
        response = self.client.get(
            self.url,
            {"ordering": "price"}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        
    def test_flash_sale_products(self):
        self.product.is_flash_sale = True
        self.product.flash_sale_discount = Decimal("20.00")
        self.product.save()

        response = self.client.get(
            "/api/products/flash-sales/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )