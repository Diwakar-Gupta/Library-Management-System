from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from lms.models import action
from lms.models.account import Account
from lms.models.book import BookItem

from .dummy_data import DummyDataMixin


class AccountPermissionTest(DummyDataMixin, TestCase):
  
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        self.abrar = User.objects.get(username='abrar')
        self.atul = User.objects.get(username='atul')
        self.librarian = User.objects.get(username='librarian')

    def test_reserve_permission(self):
        assert False == Account.can_reserve_book_for_others(self.abrar)
        assert True == Account.can_reserve_book_for_others(self.librarian)

    def test_librarian_permission(self):
        assert True == Account.is_librarian(self.librarian)
        assert False == Account.is_librarian(self.abrar)

    def test_return_permission(self):
        assert True == Account.can_return(self.librarian)
        assert False == Account.can_return(self.abrar)

    def test_checkout_permission(self):
        assert True == Account.can_checkout(self.librarian)
        assert False == Account.can_checkout(self.abrar)

    def test_see_lending_permission(self):
        abrar = User.objects.get(username='abrar')
        book_item = BookItem.objects.get(barcode='barcode123')
        due_date = datetime.now().date()
        lending = action.BookLending.check_out(abrar.account, book_item, due_date)

        assert True == Account.can_see_all_lendings(self.librarian)
        assert True == self.abrar.account.can_see_lending(lending)
        assert False == self.atul.account.can_see_lending(lending)

    def test_reservation_permission(self):
        assert False == Account.can_reserve_book_for_others(self.abrar)
        assert True == Account.can_reserve_book_for_others(self.librarian)

