from django.db import models
from django.db import transaction
from django.shortcuts import resolve_url
from lms.models import Book, BookItem, BookStatus
from lms.models import Account
from lms.models import LibraryConfig
from lms.models.notification import Notification


class ReservationStatus(models.TextChoices):
        Waiting = 'W', ('Waiting')
        Pending = 'P', ('Pending')
        Completed = 'CO', ('Completed')
        Canceled = 'CA', ('Canceled')

class BookReservationFormat(models.TextChoices):
        Hardcover = 'HC', ('Hardcover')
        Paperback = 'PB', ('Paperback')
        AudioBook = 'AB', ('AudioBook')
        EBook = 'EB', ('EBook')
        NewsPaper = 'NP', ('NewsPaper')
        ANY = 'AN', ('Any')


class BookReservation(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    # book = models.ForeignKey(Book, null=False, blank=False, on_delete=models.CASCADE)
    # book_format = models.CharField(
    #     max_length=2,
    #     choices=BookReservationFormat.choices,
    #     default=BookReservationFormat.Hardcover,
    # )
    book_item = models.ForeignKey(BookItem, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now_add=True, db_index=True)
    status = models.CharField(
        max_length=2,
        choices=ReservationStatus.choices,
        default=ReservationStatus.Waiting,
        db_index=True
    )

    def get_absolute_url(self):
        return resolve_url('reservations_detail', pk=self.pk)

    def get_status(self):
        return self.status
    
    def is_editable_by(self, user):
        return user.account == self.account or user.has_perm('lms.change_bookreservation')
    
    def cancel_reservation(self):
        self.status = ReservationStatus.Canceled
        self.save()
        notification_content = self.__class__.get_notification_content(self.account, self.book_item, reserved=False, cancelled=True)
        Notification.objects.create(account=self.account, content=notification_content)
        return self
    
    @classmethod
    def get_notification_content(cls, account, book_item, reserved=False, cancelled=False):
        if reserved:
            return f'Book with barcode {book_item.barcode} reserved successfully.'
        elif cancelled:
            return f'Reservation for Book with barcode {book_item.barcode} has been canceled.'
        assert False, 'both reserved and cancelled cant be False'
            

    @classmethod
    def reserve_book_item(cls, account, book_item):

        with transaction.atomic():
            book_item.status = BookStatus.Reserved
            book_item.save()
            obj = cls.objects.create(account=account, book_item=book_item, status=ReservationStatus.Waiting)
            notification_content = cls.get_notification_content(account, book_item, reserved=True)
            Notification.objects.create(account=account, content=notification_content)
            return obj
    
    class Meta:
        permissions = [
                ('can_reserve_for_others', "Can Reserve Book Item for other's"),
            ]


class BookLending(models.Model):
    account = models.ForeignKey(Account, blank=False, null=False, on_delete=models.CASCADE, db_index=True)
    book_item = models.ForeignKey(BookItem, blank=False, null=False, on_delete=models.CASCADE, db_index=True)
    creation_date = models.DateField(auto_now_add=True, db_index=True)
    due_date = models.DateField(db_index=True)
    return_date = models.DateField(blank=True, null=True, db_index=True)
    
    def __str__(self):
        return self.book_item.barcode
    
    def get_absolute_url(self):
        return resolve_url('lendings_detail', pk=self.pk)
    
    @classmethod
    def check_out(cls, account, book_item, due_date, notification_content=''):
        
        with transaction.atomic():
            book_lend = BookLending(account=account, book_item=book_item, due_date=due_date)
            book_lend.save()
            account.issued_book_count += 1
            account.save()
            book_item.borrowed = book_lend.creation_date
            book_item.due_date = book_lend.due_date
            book_item.status = BookStatus.Issued
            book_item.save()

            Notification.objects.create(account=account, content=notification_content).save()
            
            reservs = BookReservation.objects.filter(book_item=book_item, account=account).all()
            for reserv in reservs:
                reserv.status = ReservationStatus.Completed
                reserv.save()
        return book_lend
    
    def validate_return_data(self, return_info):
        return True, ''

    def create_return_notification(self):
        return f'Book with barcode={self.book_item.barcode} is returned'

    def return_book_item(self, return_date, notification_content=None):
        if not notification_content:
            notification_content = self.create_return_notification()

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
            
            Notification.objects.create(account=self.account, content=notification_content).save()
        return fine_amt

    def get_fine(self):
        if hasattr(self, 'fine'):
            return self.fine.amount
        else:
            return 0

    def calculate_fine(self, return_date):
        late_by = (return_date - self.due_date).days
        late_by = max(late_by, 0)
        return late_by * LibraryConfig.object().fine_per_late_day

    def get_return_date(self):
        return self.return_date if self.return_date else None

