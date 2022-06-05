from datetime import datetime

from rest_framework.test import force_authenticate
from rest_framework.test import APITestCase
from rest_framework import status

from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.test import Client

from lms.views import book
from .dummy_data import DummyDataMixin


class BookListTest(DummyDataMixin, TestCase):
  
    def setUp(self):
        self.factory = RequestFactory()
        self.student = User.objects.get(username='abrar')
        self.librarian = User.objects.get(username='librarian')
        self.client = Client()

    def test_books_list(self):
        view = book.BookListView.as_view()

        request = self.factory.get('/books/')
        force_authenticate(request, user=self.student)
        response = view(request)
        assert response.status_code == status.HTTP_200_OK

    def test_book_detail_auth(self):
        response = self.client.get('/book/453678754/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        self.client.force_login(self.student)
        response = self.client.get('/book/453678754/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_book_detail_not_found(self):
        view = book.BookDetail.as_view()

        request = self.factory.get('/book/')
        force_authenticate(request, user=self.student)
        response = view(request, **{'isbn': '-1'})
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_book_issue(self):

        self.client.force_login(self.librarian)

        post_data = {
            'account': self.student.account.id,
            'book_item': 'barcode123',
            'bypass_issue_quota': 'false',
            }
        response = self.client.post('/book-item/issue/', data=post_data)
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_book_issue_by_student(self):

        self.client.force_login(self.student)

        post_data = {
            'account': self.student.account.id,
            'book_item': 'barcode123',
            'bypass_issue_quota': 'false',
            }
        response = self.client.post('/book-item/issue/', data=post_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_book_issue_invalid_data(self):

        self.client.force_login(self.librarian)

        post_data = {
            'account': self.student.account.id,
            'book_item': 'barcode123-1',
            'bypass_issue_quota': 'false',
            }
        response = self.client.post('/book-item/issue/', data=post_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    