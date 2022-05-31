from django.db import models
from lms.models.account import AccountStatus
from django.db import transaction


class Book(models.Model):
    isbn = models.CharField(max_length=13, primary_key=True)
    title = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    publisher = models.CharField(max_length=50)
    language = models.CharField(max_length=30)
    numer_of_pages = models.PositiveIntegerField(verbose_name='Number of pages in Book', )

    def __str__(self):
        return self.title

    def get_title(self):
        return self.title
    
    def is_accessible_by(self, account):
        if account is None:
            return False
        return account.status == AccountStatus.Active


class Rack(models.Model):
    number = models.PositiveIntegerField(verbose_name='Number')
    location_identifier = models.CharField(max_length=12, verbose_name='Location Identifier')


class BookFormat(models.TextChoices):
        Hardcover = 'HC', ('Hardcover')
        Paperback = 'PB', ('Paperback')
        AudioBook = 'AB', ('AudioBook')
        EBook = 'EB', ('EBook')
        NewsPaper = 'NP', ('NewsPaper')

class BookStatus(models.TextChoices):
        Available = 'AV', ('Available')
        Reserved = 'RE', ('Reserved')
        Issued = 'IS', ('Issued')
        Lost = 'LO', ('Lost')


class BookItem(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    barcode = models.CharField(max_length=12, primary_key=True)
    is_reference_only = models.BooleanField()
    borrowed = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    price = models.PositiveIntegerField()
    format = models.CharField(
        max_length=2,
        choices=BookFormat.choices,
        default=BookFormat.Hardcover,
    )
    status = models.CharField(
        max_length=2,
        choices=BookStatus.choices,
        default=BookStatus.Available,
    )
    date_of_purchase = models.DateField(verbose_name='Purchase Date')
    publication_date = models.DateField(null=True, blank=True, verbose_name='Publication Date')
    
    placed_at = models.OneToOneField(Rack, on_delete=models.CASCADE, verbose_name='Placed At')

    class Meta:
        permissions = [
                ('can_checkout_book_item', 'Can CheckOut Book Item'),
                ('can_return_book_item', 'Can Return Book Item'),
                ('can_renew_book_item', 'Can Renew Book Item'),
            ]
    
    def get_title(self):
        return self.book.title
    
    def get_lending_object(self):
        if not self.borrowed:
            return None
        else:
            self.booklending_set.get(return_date=None)

    def return_book_item(self):
        # TODO
        return False

    @classmethod
    def check_out(cls, account, book_item, due_date):
        from lms.models import BookLending, BookReservation, ReservationStatus
        
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
            return book_lend.pk
    
    def is_reserved(self):
        return self.status == BookStatus.Reserved
    
    def can_be_issued(self):
        return not self.is_reference_only and self.status == BookStatus.Available

