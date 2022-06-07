from datetime import datetime

from rest_framework import status

from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.test import Client
from django.shortcuts import resolve_url

from lms.models import action
from lms.models.book import BookItem

from .dummy_data import DummyDataMixin


class LendingTest(DummyDataMixin, TestCase):
  
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        abrar = User.objects.get(username='abrar')
        book_item = BookItem.objects.get(barcode='barcode123')
        due_date = datetime.now().date()
        action.BookLending.check_out(abrar.account, book_item, due_date)

    def setUp(self):
        self.factory = RequestFactory()
        self.abrar = User.objects.get(username='abrar')
        self.atul = User.objects.get(username='atul')
        self.librarian = User.objects.get(username='librarian')
        self.abrar_lending = action.BookLending.objects.all()[0]
        self.client = Client()

    def test_lending_list(self):
        response = self.client.get(resolve_url('lendings_list'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        self.client.force_login(self.atul)
        response = self.client.get(resolve_url('lendings_list'))
        assert response.status_code == status.HTTP_200_OK
    
    def test_lending_detail(self):
        response = self.client.get(resolve_url('lendings_detail', pk=self.abrar_lending.pk))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        self.client.force_login(self.atul)
        response = self.client.get(resolve_url('lendings_detail', pk=self.abrar_lending.pk))
        assert response.status_code == status.HTTP_403_FORBIDDEN

        self.client.force_login(self.abrar)
        response = self.client.get(resolve_url('lendings_detail', pk=self.abrar_lending.pk))
        assert response.status_code == status.HTTP_200_OK

    def test_lending_detail_barcode(self):
        url = resolve_url('lendings_return', barcode=self.abrar_lending.book_item.pk)

        response = self.client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        self.client.force_login(self.atul)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

        self.client.force_login(self.abrar)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        self.client.force_login(self.librarian)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        

    def test_user_lendings_unauth(self):
        url = resolve_url('my_lendings_list')

        response = self.client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_my_lendings_redirect(self):
        url = resolve_url('my_lendings_list')

        self.client.force_login(self.atul)
        response = self.client.get(url, follow=True)
        assert response.status_code == status.HTTP_200_OK

    def test_my_lendings(self):
        self.client.force_login(self.abrar)
        response = self.client.get(resolve_url('user_lendings_list', id=self.abrar.account.id))
        assert response.status_code == status.HTTP_200_OK

    def test_other_lendings(self):
        self.client.force_login(self.atul)
        response = self.client.get(resolve_url('user_lendings_list', id=self.abrar.account.id))
        assert response.status_code == status.HTTP_403_FORBIDDEN

