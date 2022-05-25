from django.db import models


class Book(models.Model):
    ISBN = models.CharField(max_length=13, primary_key=True)
    title = models.CharField(max_length=30)
    subject = models.CharField(max_length=30)
    publisher = models.CharField(max_length=30)
    language = models.CharField(max_length=30)
    numer_of_pages = models.PositiveIntegerField(verbose_name='Number of pages in Book', )

    def __str__(self):
        return self.title

    def get_title(self):
        return self.title


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
        Lost = 'LO', ('Lost')

class BookItem(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    barcode = models.CharField(max_length=12, primary_key=True)
    is_reference_only = models.BooleanField()
    borrowed = models.DateField(null=True, default=None)
    due_date = models.DateField(null=True, default=None)
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
    publication_date = models.DateField(null=True, verbose_name='Publication Date')
    
    placed_at = models.ForeignKey(Rack, on_delete=models.CASCADE, verbose_name='Placed At')


    class Meta:
        permissions = [
                ('can_checkout_book_item', 'Can CheckOut Book Item'),
                ('can_checkin_book_item', 'Can CheckIn Book Item'),
            ]

    def check_in(self):
        # TODO
        return False

    def check_out(self):
        # TODO
        return False
