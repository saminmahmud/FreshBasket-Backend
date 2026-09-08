from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from tests.base import BaseTestCase
from apps.orders.models import Order, OrderItem, DeliveryCharge
from apps.products.models import Category, Product

User = get_user_model()

class OrdersAPITestCase(BaseTestCase, APITestCase):
    def setUp(self):
        self.user = self.create_user(
            username="customer",
            password="password123",
            verified=True,
        )

        self.category = Category.objects.create(
            name="Fruits"
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

        DeliveryCharge.objects.create(
            delivery_area="inside_dhaka",
            charge_amount=Decimal("60.00"),
        )

        self.url = "/api/orders/"

        self.order_data = {
            "full_name": "Test Customer",
            "phone": "01700000000",
            "address": "Test Address",
            "latitude": "23.8103000",
            "longitude": "90.4125000",
            "city": "Dhaka",
            "postal_code": "1200",
            "payment_method": "cash_on_delivery",
            "delivery_area": "inside_dhaka",
            "items": [
                {
                    "product_id": self.product.id,
                    "quantity": 2,
                }
            ],
        }

    def test_create_order_requires_authentication(self):
        response = self.client.post(
            self.url,
            data=self.order_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_create_cash_on_delivery_order(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            data=self.order_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertIn(
            "order_id",
            response.data,
        )

        order = Order.objects.get(
            id=response.data["order_id"]
        )

        self.assertEqual(
            order.user,
            self.user,
        )

        self.assertEqual(
            order.payment_method,
            "cash_on_delivery",
        )

        self.assertEqual(
            order.order_status,
            "pending",
        )

        self.assertEqual(
            order.subtotal,
            Decimal("180.00"),
        )

        self.assertEqual(
            order.delivery_charge,
            Decimal("60.00"),
        )

        self.assertEqual(
            order.total_price,
            Decimal("240.00"),
        )

        self.assertTrue(
            order.tracking_code
        )

        self.assertTrue(
            OrderItem.objects.filter(
                order=order,
                product=self.product,
                quantity=2,
                price=Decimal("180.00"),
            ).exists()
        )

    def test_create_order_without_delivery_charge(self):
        DeliveryCharge.objects.all().delete()

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            data=self.order_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        order = Order.objects.get(
            id=response.data["order_id"]
        )

        self.assertEqual(
            order.delivery_charge,
            Decimal("0.00"),
        )

        self.assertEqual(
            order.total_price,
            Decimal("180.00"),
        )

    def test_user_can_see_own_orders(self):
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
            delivery_area="inside_dhaka",
            subtotal=Decimal("100.00"),
        )

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["id"],
            order.id,
        )

    def test_user_cannot_see_other_users_orders(self):
        other_user = self.create_user(
            username="other_customer",
            email="other@example.com",
            password="password123",
            verified=True,
        )

        Order.objects.create(
            user=other_user,
            full_name="Other Customer",
            phone="01800000000",
            address="Other Address",
            latitude=Decimal("23.8103000"),
            longitude=Decimal("90.4125000"),
            city="Dhaka",
            postal_code="1200",
            payment_method="cash_on_delivery",
            delivery_area="inside_dhaka",
            subtotal=Decimal("100.00"),
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            0,
        )

    def test_admin_can_see_all_orders(self):
        admin = self.create_user(
            username="admin",
            email="admin@example.com",
            password="password123",
            verified=True,
        )
        admin.is_staff = True
        admin.save()

        other_user = self.create_user(
            username="other_customer",
            email="other@example.com",
            password="password123",
            verified=True,
        )

        Order.objects.create(
            user=self.user,
            full_name="Customer One",
            phone="01700000000",
            address="Address One",
            latitude=Decimal("23.8103000"),
            longitude=Decimal("90.4125000"),
            city="Dhaka",
            postal_code="1200",
            payment_method="cash_on_delivery",
            delivery_area="inside_dhaka",
            subtotal=Decimal("100.00"),
        )

        Order.objects.create(
            user=other_user,
            full_name="Customer Two",
            phone="01800000000",
            address="Address Two",
            latitude=Decimal("23.8103000"),
            longitude=Decimal("90.4125000"),
            city="Dhaka",
            postal_code="1200",
            payment_method="cash_on_delivery",
            delivery_area="inside_dhaka",
            subtotal=Decimal("200.00"),
        )

        self.client.force_authenticate(
            user=admin
        )

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

    def test_create_order_with_multiple_items(self):
        banana = Product.objects.create(
            name="Banana",
            description="Fresh banana",
            price=Decimal("50.00"),
            category=self.category,
            unit="kg",
            unit_quantity=Decimal("1.00"),
            stock=20,
        )

        self.client.force_authenticate(
            user=self.user
        )

        data = {
            **self.order_data,
            "items": [
                {
                    "product_id": self.product.id,
                    "quantity": 2,
                },
                {
                    "product_id": banana.id,
                    "quantity": 3,
                },
            ],
        }

        response = self.client.post(
            self.url,
            data=data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        order = Order.objects.get(
            id=response.data["order_id"]
        )

        # Apple: 90 * 2 = 180
        # Banana: 50 * 3 = 150
        # Total subtotal = 330
        self.assertEqual(
            order.subtotal,
            Decimal("330.00"),
        )

        self.assertEqual(
            order.items.count(),
            2,
        )

    def test_order_detail(self):
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
            delivery_area="inside_dhaka",
            subtotal=Decimal("100.00"),
        )

        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            price=Decimal("90.00"),
        )

        response = self.client.get(
            f"{self.url}{order.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            order.id,
        )

        self.assertEqual(
            len(response.data["items"]),
            1,
        )

        self.assertEqual(
            response.data["items"][0]["product"]["name"],
            "Apple",
        )

    def test_user_cannot_access_other_users_order_detail(self):
        other_user = self.create_user(
            username="other_customer",
            email="other@example.com",
            password="password123",
            verified=True,
        )

        order = Order.objects.create(
            user=other_user,
            full_name="Other Customer",
            phone="01800000000",
            address="Other Address",
            latitude=Decimal("23.8103000"),
            longitude=Decimal("90.4125000"),
            city="Dhaka",
            postal_code="1200",
            payment_method="cash_on_delivery",
            delivery_area="inside_dhaka",
            subtotal=Decimal("100.00"),
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            f"{self.url}{order.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_admin_can_update_order_status(self):
        admin = self.create_user(
            username="admin",
            email="admin@example.com",
            password="password123",
            verified=True,
            role="delivery_partner",
        )
        admin.is_staff = True
        admin.save()
        
        self.client.force_authenticate(user=self.user)

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
            delivery_area="inside_dhaka",
            order_status="assigned_to_delivery",
            subtotal=Decimal("100.00"),
        )

        self.client.force_authenticate(
            user=admin
        )

        response = self.client.patch(
            f"/api/order-status-update/{order.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        order.refresh_from_db()

        self.assertEqual(
            order.order_status,
            "packed",
        )

    def test_order_status_update_requires_otp_before_delivery(self):
        admin = self.create_user(
            username="admin",
            email="admin@example.com",
            password="password123",
            verified=True,
            role="delivery_partner",
        )
        admin.is_staff = True
        admin.save()
        
        self.client.force_authenticate(user=self.user)

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
            delivery_area="inside_dhaka",
            order_status="out_for_delivery",
            is_otp_verified=False,
            subtotal=Decimal("100.00"),
        )

        self.client.force_authenticate(
            user=admin
        )

        response = self.client.patch(
            f"/api/order-status-update/{order.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            response.data["error"],
            "OTP verification required before marking as delivered",
        )

    def test_order_cancel(self):
        admin = self.create_user(
            username="admin",
            email="admin@example.com",
            password="password123",
            verified=True,
            role="delivery_partner",
        )
        admin.is_staff = True
        admin.save()
        
        self.client.force_authenticate(user=self.user)

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
            delivery_area="inside_dhaka",
            order_status="confirmed",
            subtotal=Decimal("100.00"),
        )

        self.client.force_authenticate(
            user=admin
        )

        response = self.client.patch(
            f"/api/order-cancel/{order.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        order.refresh_from_db()

        self.assertEqual(
            order.order_status,
            "cancelled",
        )

    def test_cannot_cancel_delivered_order(self):
        admin = self.create_user(
            username="admin",
            email="admin@example.com",
            password="password123",
            verified=True,
            role="delivery_partner",
        )
        admin.is_staff = True
        admin.save()
        
        self.client.force_authenticate(user=self.user)

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
            delivery_area="inside_dhaka",
            order_status="delivered",
            subtotal=Decimal("100.00"),
        )

        self.client.force_authenticate(
            user=admin
        )

        response = self.client.patch(
            f"/api/order-cancel/{order.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        order.refresh_from_db()

        self.assertEqual(
            order.order_status,
            "delivered",
        )

    def test_order_tracking(self):
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
            delivery_area="inside_dhaka",
            subtotal=Decimal("100.00"),
            tracking_code="TRACK123",
        )

        response = self.client.get(
            "/api/orders/tracking/TRACK123/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["data"]["tracking_code"],
            "TRACK123",
        )

        self.assertEqual(
            response.data["data"]["order_status"],
            "pending",
        )

    def test_order_tracking_invalid_code(self):
        response = self.client.get(
            "/api/orders/tracking/INVALID123/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertEqual(
            response.data["message"],
            "No order found with this tracking code",
        )

    def test_admin_dashboard(self):
        admin = self.create_user(
            username="admin",
            email="admin@example.com",
            password="password123",
            verified=True,
        )
        admin.is_staff = True
        admin.save()

        Order.objects.create(
            user=self.user,
            full_name="Test Customer",
            phone="01700000000",
            address="Test Address",
            latitude=Decimal("23.8103000"),
            longitude=Decimal("90.4125000"),
            city="Dhaka",
            postal_code="1200",
            payment_method="cash_on_delivery",
            delivery_area="inside_dhaka",
            subtotal=Decimal("100.00"),
        )

        self.client.force_authenticate(
            user=admin
        )

        response = self.client.get(
            "/api/admin-dashboard/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["total_orders"],
            1,
        )

        self.assertEqual(
            response.data["total_users"],
            User.objects.count(),
        )

        self.assertEqual(
            response.data["total_products"],
            Product.objects.count(),
        )

    def test_admin_dashboard_requires_admin(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            "/api/admin-dashboard/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
