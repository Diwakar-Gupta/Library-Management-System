from django.shortcuts import resolve_url
from rest_framework.test import force_authenticate
from rest_framework import status

from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.test import Client
from lms.models.action import BookLending
from lms.models.book import BookItem, BookStatus

from lms.views import book
from .dummy_data import DummyDataMixin


class BookListTest(DummyDataMixin, TestCase):
  
    def setUp(self):
        self.factory = RequestFactory()
        self.student = User.objects.get(username='abrar')
        self.atul = User.objects.get(username='atul')
        self.abrar = User.objects.get(username='abrar')
        self.librarian = User.objects.get(username='librarian')
        self.client = Client()

    def test_books_list(self):
        view = book.BookListView.as_view()

        url = resolve_url('book_list')

        request = self.factory.get(url)
        force_authenticate(request, user=self.student)
        response = view(request)
        assert response.status_code == status.HTTP_200_OK

    def test_book_detail_auth(self):
        response = self.client.get('/api/book/453678754/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        self.client.force_login(self.student)
        response = self.client.get('/api/book/453678754/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_book_detail_not_found(self):
        view = book.BookDetail.as_view()

        request = self.factory.get('/api/book/')
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
        response = self.client.post('/api/book-item/issue/', data=post_data)
        assert response.status_code == status.HTTP_201_CREATED

        book_lending = BookLending.objects.get(pk=response.data['pk'])
        assert book_lending.return_date == None
        assert BookItem.objects.get(pk=book_lending.book_item.barcode).status == BookStatus.Issued
    
    def test_book_issue_by_student(self):

        self.client.force_login(self.student)

        post_data = {
            'account': self.student.account.id,
            'book_item': 'barcode123',
            'bypass_issue_quota': 'false',
            }
        response = self.client.post('/api/book-item/issue/', data=post_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_issue_reference_book(self):

        self.client.force_login(self.librarian)

        post_data = {
            'account': self.student.account.id,
            'book_item': 'barcode123-1', # reference book
            'bypass_issue_quota': 'false',
            }
        response = self.client.post('/api/book-item/issue/', data=post_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_book_return_auth(self):

        book_lending = self.issue_book(account=self.abrar.account.id)
        assert book_lending.return_date == None

        url = '/api/lendings/barcode/{}/'.format(book_lending.book_item.barcode)
        post_data = {}

        self.client.force_login(self.atul)
        response = self.client.post(url, data=post_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

        self.client.force_login(self.abrar)
        response = self.client.post(url, data=post_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
        self.client.force_login(self.librarian)
        response = self.client.post(url, data=post_data)
        assert response.status_code == status.HTTP_200_OK

        assert BookLending.objects.get(pk=book_lending.pk).return_date != None
        assert BookItem.objects.get(pk=book_lending.book_item.pk).status == BookStatus.Available

    def issue_book(self, account=None, book_item='barcode123', bypass_issue_quota=False):
        if account == None:
            account = self.abrar.account.id
        
        self.client.force_login(self.librarian)

        post_data = {
            'account': account,
            'book_item': book_item,
            'bypass_issue_quota': bypass_issue_quota,
            }
        response = self.client.post('/api/book-item/issue/', data=post_data)
        assert response.status_code == status.HTTP_201_CREATED
        book_lending = BookLending.objects.get(account__id=account, book_item__barcode=book_item, return_date=None)
        return book_lending

