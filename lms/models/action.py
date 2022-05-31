from django.db import models
from lms.models import Book, BookItem
from lms.models import Account

class ReservationStatus(models.TextChoices):
        Waiting = 'W', ('Waiting')
        Pending = 'P', ('Pending')
        Completed = 'COM', ('Completed')
        Canceled = 'CAN', ('Canceled')

class BookReservationFormat(models.TextChoices):
        Hardcover = 'HC', ('Hardcover')
        Paperback = 'PB', ('Paperback')
        AudioBook = 'AB', ('AudioBook')
        EBook = 'EB', ('EBook')
        NewsPaper = 'NP', ('NewsPaper')
        ANY = 'AN', ('Any')

class BookReservation(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, null=False, blank=False, on_delete=models.CASCADE)
    book_format = models.CharField(
        max_length=2,
        choices=BookReservationFormat.choices,
        default=BookReservationFormat.Hardcover,
    )
    creation_date = models.DateField()
    status = models.CharField(
        max_length=4,
        choices=ReservationStatus.choices,
        default=ReservationStatus.Waiting,
    )

    def get_status(self):
        # TODO
        return None

    def fetch_reservation_details(self):
        # TODO
        return None


class BookLending(models.Model):
    account = models.ForeignKey(Account, blank=False, null=False, on_delete=models.CASCADE)
    book_item = models.ForeignKey(BookItem, blank=False, null=False, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return self.book_item.barcode

    def get_return_date(self):
        # TODO
        return None