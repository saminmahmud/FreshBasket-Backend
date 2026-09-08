from rest_framework import status
from rest_framework.test import APITestCase
from tests.base import BaseTestCase
from apps.products.models import Category


class CategoryAPITestCase(BaseTestCase, APITestCase):
    def setUp(self):
        self.url = "/api/categories/"
        
        self.category = Category.objects.create(
            name="Fruits",
        )
        
        self.user = self.create_user(
            username="customer",
            password="Password123@",
        )
    
    def test_list_categories(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_create_category_requires_admin(self):
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(
            self.url,
            data={
                "name": "Vegetables",
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_create_category_as_admin(self):
            self.user.is_staff = True
            self.user.save()
            self.client.force_authenticate(user=self.user)
            
            response = self.client.post(
                self.url,
                data={
                    "name": "Vegetables",
                },
                format='json'
            )
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(Category.objects.filter(name="Vegetables").exists())
            
    def test_update_category_requires_admin(self):
        self.client.force_authenticate(user=self.user)
        
        response = self.client.put(
            f"{self.url}{self.category.id}/",
            data={
                "name": "Updated Fruits",
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    
    def test_delete_category_requires_admin(self):
        self.client.force_authenticate(user=self.user)
        
        response = self.client.delete(f"{self.url}{self.category.id}/")
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
        
    