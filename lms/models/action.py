from django.db import models
from django.db import transaction
from lms.models import Book, BookItem, BookStatus
from lms.models import Account
from lms.models import LibraryConfig


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
    
    @classmethod
    def check_out(cls, account, book_item, due_date):
        
        with transaction.atomic():
            book_lend = BookLending(account=account, book_item=book_item, due_date=due_date)
            book_lend.save()
            account.issued_book_count += 1
            account.save()
            book_item.borrowed = book_lend.creation_date
            book_item.due_date = book_lend.due_date
            book_item.status = BookStatus.Issued
            book_item.save()
            
            reservs = BookReservation.objects.filter(book=book_item.book, account=account).all()
            for reserv in reservs:
                reserv.status = ReservationStatus.Completed
                reserv.save()
        return book_lend
    
    def return_book_item(self, return_date):
        with transaction.atomic():
            self.return_date = return_date
            
            self.account.issued_book_count -= 1
            
            self.book_item.borrowed = None
            self.book_item.due_date = None
            self.book_item.status = BookStatus.Available

            self.save()
            self.account.save()
            self.book_item.save()

            fine_amt = self.calculate_fine(return_date)
            if fine_amt > 0:
                from lms.models import Fine
                fine = Fine(amount=fine_amt, lending = self)
                fine.save()
        return fine_amt


    def get_fine(self):
        if self.fine:
            return self.fine.amount
        else:
            return 0

    def calculate_fine(self, return_date):
        late_by = (return_date - self.due_date).days
        late_by = max(late_by, 0)
        return late_by * LibraryConfig.object().fine_per_late_day

    def get_return_date(self):
        return self.return_date if self.return_date else None