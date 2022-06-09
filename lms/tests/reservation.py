from datetime import datetime
import json

from rest_framework.test import force_authenticate
from rest_framework import status

from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.test import Client
from django.shortcuts import resolve_url

from lms.models.account import Account
from lms.models.action import BookReservation, ReservationStatus
from lms.models.book import BookItem, Book, Rack

from lms.views import book, reservation
from .dummy_data import DummyDataMixin


class ReservationTest(DummyDataMixin, TestCase):
  
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        book2 = Book.objects.create(isbn='453678755', title='The Kaggle Book', subject='Data Science', publisher='Push', language='Englist', numer_of_pages=89)
        BookItem.objects.create(book=book2, barcode='barcode-55', is_reference_only=False, price=102, date_of_purchase=datetime.now().date(), placed_at=Rack.objects.create(number=9, location_identifier='AQ'))
        BookItem.objects.create(book=book2, barcode='barcode-89', is_reference_only=False, price=102, date_of_purchase=datetime.now().date(), placed_at=Rack.objects.create(number=10, location_identifier='AQ'))
        
        account = Account.objects.get(id=30)
        BookReservation.reserve_book_item(account, BookItem.objects.get(barcode='barcode-55'))

    def setUp(self):
        self.factory = RequestFactory()
        self.abrar = User.objects.get(username='abrar')
        self.atul = User.objects.get(username='atul')
        self.librarian = User.objects.get(username='librarian')
        self.abrar_reserv = BookReservation.objects.all()[0]
        self.client = Client()

    def test_reservation_list(self):
        view = reservation.AllReservations.as_view()

        request = self.factory.get('/api/reservations/')
        force_authenticate(request, user=self.abrar)
        response = view(request)
        assert response.status_code == status.HTTP_200_OK

    def test_reservation_detail_auth(self):
        response = self.client.get('/api/reservations/{}/'.format(self.abrar_reserv.pk))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        self.client.force_login(self.atul)
        response = self.client.get('/api/reservations/{}/'.format(self.abrar_reserv.pk))
        assert response.status_code == status.HTTP_403_FORBIDDEN

        self.client.force_login(self.abrar)
        response = self.client.get('/api/reservations/{}/'.format(self.abrar_reserv.pk))
        assert response.status_code == status.HTTP_200_OK
            
    def test_reservation_detail_not_found(self):
        self.client.force_login(self.abrar)
        response = self.client.get('/api/reservations/878/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_reserve_creation(self):

        post_data = {
            'account': self.atul.account.id,
            'book_item': 'barcode123',
            }
        
        self.client.force_login(self.abrar)
        response = self.client.post('/api/book-item/reserve/', data=post_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

        post_data['book_item'] = 'barcode123-1'
        self.client.force_login(self.atul)
        response = self.client.post('/api/book-item/reserve/', data=post_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        post_data['book_item'] = 'barcode-89'
        self.client.force_login(self.librarian)
        response = self.client.post('/api/book-item/reserve/', data=post_data)
        assert response.status_code == status.HTTP_201_CREATED

        post_data['book_item'] = 'barcode123'
        self.client.force_login(self.atul)
        response = self.client.post('/api/book-item/reserve/', data=post_data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_reserve_creation_invalid_data(self):

        post_data = {
            'account': -1,
            'book_item': 'barcode123',
            }
        
        self.client.force_login(self.librarian)
        response = self.client.post('/api/book-item/reserve/', data=post_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        post_data = {
            'account': self.atul.account.id,
            'book_item': '-1',
            }

        self.client.force_login(self.librarian)
        response = self.client.post('/api/book-item/reserve/', data=post_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_reservation_detail_barcode(self):
        self.client.force_login(self.abrar)
        response = self.client.get('/api/reservations/barcode/{}/'.format(self.abrar_reserv.book_item.barcode))
        assert response.status_code == status.HTTP_200_OK
    
    def test_cancel_reservation(self):
        pk = BookReservation.reserve_book_item(account=self.atul.account, book_item=BookItem.objects.get(barcode='barcode-89')).pk
        post_data = {
            'status': 'canceled',
            }
        
        self.client.force_login(self.abrar)
        response = self.client.put(
            f'/api/reservations/{pk}/',
            data=json.dumps(post_data),
            content_type = 'application/json'
            )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        assert self.abrar_reserv.status == ReservationStatus.Waiting
        self.client.force_login(self.atul)
        response = self.client.put(
            resolve_url('reservations_detail', pk=pk),
            data=json.dumps(post_data),
            content_type = 'application/json'
            )
        assert response.status_code == status.HTTP_200_OK
        assert BookReservation.objects.get(pk=pk).status == ReservationStatus.Canceled

