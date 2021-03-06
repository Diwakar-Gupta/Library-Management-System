from django.db import models
from django.shortcuts import resolve_url
from lms.models.account import AccountStatus


class Book(models.Model):
    isbn = models.CharField(max_length=13, primary_key=True, db_index=True)
    title = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    publisher = models.CharField(max_length=50)
    language = models.CharField(max_length=30)
    numer_of_pages = models.PositiveIntegerField(verbose_name='Number of pages in Book', )

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return resolve_url('book_detail', isbn=self.isbn)

    def get_title(self):
        return self.title
    
    def is_accessible_by(self, user):
        if user.has_perm('lms.view_book'):
            return True
        elif hasattr(user, 'account'):
            return user.account.status == AccountStatus.Active
    
    # can be cached for some time
    def count_total_bookitems(self):
        return BookItem.objects.filter(book=self).count()

    # can be cached for some time
    def count_available_bookitems(self):
        return BookItem.objects.filter(book=self, status=BookStatus.Available).count()

    # can be cached for some time
    def count_issued_bookitems(self):
        return BookItem.objects.filter(book=self, status=BookStatus.Issued).count()

    # can be cached for some time
    def count_reserved_bookitems(self):
        return BookItem.objects.filter(book=self, status=BookStatus.Reserved).count()

    # can be cached for some time
    def count_lost_bookitems(self):
        return BookItem.objects.filter(book=self, status=BookStatus.Lost).count()


class Rack(models.Model):
    number = models.PositiveIntegerField(verbose_name='Number')
    location_identifier = models.CharField(max_length=12, verbose_name='Location Identifier')

    def __str__(self):
        return "{} {}".format(self.location_identifier, self.number)
    
    class Meta:
        unique_together = ("number", "location_identifier")


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
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_index=True)
    barcode = models.CharField(max_length=12, primary_key=True, db_index=True)
    is_reference_only = models.BooleanField(default=False, help_text="This book can't be issued.")
    borrowed = models.DateField(blank=True, null=True, db_index=True)
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
        db_index=True
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
    
    def get_absolute_url(self):
        return resolve_url('book_item_list')+'?barcode={}'.format(self.barcode)

    def get_title(self):
        return self.book.title
    
    def get_lending_object(self):
        if not self.borrowed:
            return None
        else:
            self.booklending_set.get(return_date=None)

    def can_be_reserved(self):
        if self.is_reference_only:
            return False, 'Reference only Book'
        if self.status == BookStatus.Reserved:
            return False, 'Already Reserved'
        if self.status == BookStatus.Reserved:
            return False, 'Book has Lost status'
        return True, ''

    def is_reserved(self):
        return self.status == BookStatus.Reserved

    def can_be_issued(self):
        return not self.is_reference_only and self.status == BookStatus.Available

