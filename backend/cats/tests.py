from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Cat


class CatTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(username='owner')
        self.reader = user_model.objects.create_user(username='reader')
        self.client.force_authenticate(self.owner)
        self.data = {'name': 'Кекс', 'color': '#000000', 'birth_year': 2022}

    def test_owner_can_create_and_change_cat(self):
        response = self.client.post('/api/cats/', self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        cat = Cat.objects.get(pk=response.data['id'])
        self.assertEqual(cat.owner, self.owner)
        url = f'/api/cats/{cat.pk}/'
        response = self.client.patch(url, {'name': 'Макс'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cat.refresh_from_db()
        self.assertEqual(cat.name, 'Макс')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_other_user_can_only_view_cat(self):
        cat = Cat.objects.create(owner=self.owner, **self.data)
        url = f'/api/cats/{cat.pk}/'
        self.client.force_authenticate(self.reader)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)
        response = self.client.patch(url, {'name': 'Макс'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_403_FORBIDDEN)
