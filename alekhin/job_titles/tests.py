from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import JobTitle

User = get_user_model()


class JobTitleModelTest(TestCase):
    def test_create_job_title(self):
        """Тест создания должности"""
        job_title = JobTitle.objects.create(name="Косметолог")
        self.assertEqual(job_title.name, "Косметолог")
        self.assertEqual(str(job_title), "Косметолог")

    def test_unique_name(self):
        """Тест уникальности названия"""
        JobTitle.objects.create(name="Косметолог")
        with self.assertRaises(Exception):
            JobTitle.objects.create(name="Косметолог")


class JobTitleAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.job_title = JobTitle.objects.create(name="Косметолог")
        
    def get_token(self):
        """Получение JWT токена для пользователя"""
        refresh = RefreshToken.for_user(self.user)
        return str(refresh.access_token)

    def test_get_job_titles_without_token(self):
        """Тест получения списка должностей без токена"""
        url = reverse('job-titles-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_get_job_title_detail_without_token(self):
        """Тест получения детальной информации без токена"""
        url = reverse('job-titles-detail', kwargs={'pk': self.job_title.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Косметолог")

    def test_create_job_title_without_token(self):
        """Тест создания должности без токена (должно быть запрещено)"""
        url = reverse('job-titles-list')
        data = {'name': 'Флеболог'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_job_title_with_token(self):
        """Тест создания должности с токеном"""
        url = reverse('job-titles-list')
        data = {'name': 'Флеболог'}
        token = self.get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Флеболог')

    def test_update_job_title_without_token(self):
        """Тест обновления должности без токена (должно быть запрещено)"""
        url = reverse('job-titles-detail', kwargs={'pk': self.job_title.pk})
        data = {'name': 'Новый Косметолог'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_job_title_with_token(self):
        """Тест обновления должности с токеном"""
        url = reverse('job-titles-detail', kwargs={'pk': self.job_title.pk})
        data = {'name': 'Новый Косметолог'}
        token = self.get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Новый Косметолог')