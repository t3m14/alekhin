from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import ServiceType

User = get_user_model()


class ServiceTypeModelTest(TestCase):
    def test_create_service_type(self):
        """Тест создания типа услуги"""
        service_type = ServiceType.objects.create(name="Консультация")
        self.assertEqual(service_type.name, "Консультация")
        self.assertEqual(str(service_type), "Консультация")

    def test_unique_name(self):
        """Тест уникальности названия"""
        ServiceType.objects.create(name="Консультация")
        with self.assertRaises(Exception):
            ServiceType.objects.create(name="Консультация")


class ServiceTypeAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.service_type = ServiceType.objects.create(name="Консультация")
        
    def get_token(self):
        """Получение JWT токена для пользователя"""
        refresh = RefreshToken.for_user(self.user)
        return str(refresh.access_token)

    def test_get_service_types_without_token(self):
        """Тест получения списка типов услуг без токена"""
        url = reverse('service-types-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_get_service_type_detail_without_token(self):
        """Тест получения детальной информации без токена"""
        url = reverse('service-types-detail', kwargs={'pk': self.service_type.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Консультация")

    def test_create_service_type_without_token(self):
        """Тест создания типа услуги без токена (должно быть запрещено)"""
        url = reverse('service-types-list')
        data = {'name': 'Шлифовка'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_service_type_with_token(self):
        """Тест создания типа услуги с токеном"""
        url = reverse('service-types-list')
        data = {'name': 'Шлифовка'}
        token = self.get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Шлифовка')
    def test_update_service_type_with_token(self):
        """Тест обновления типа услуги с токеном"""
        url = reverse('service-types-detail', kwargs={'pk': self.service_type.pk})
        data = {'name': 'Новое название'}
        token = self.get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Новое название')