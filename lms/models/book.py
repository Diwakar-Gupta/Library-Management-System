from django.db import models

# Create your models here.
class Book(models.Model):
    ISBN = models.CharField(max_length=13, primary_key=True)
    title = models.CharField(max_length=30)
    subject = models.CharField(max_length=30)
    publisher = models.CharField(max_length=30)
    language = models.CharField(max_length=30)
    numer_of_pages = models.PositiveIntegerField(verbose_name='Number of pages in Book')

    def get_title(self):
        return self.title


class BookFormat(models.TextChoices):
        Hardcover = 'HC', ('Hardcover')
        Paperback = 'PB', ('Paperback')
        AudioBook = 'AUD', ('AudioBook')
        EBook = 'EB', ('EBook')
        NewsPaper = 'NEWS', ('NewsPaper')

class BookStatus(models.TextChoices):
        Available = 'AV', ('Available')
        Reserved = 'RES', ('Reserved')
        Lost = 'LST', ('Lost')

class BookItem(models.Model):
    barcode = models.CharField(max_length=12, primary_key=True)
    is_reference_only = models.BooleanField()
    borrowed = models.DateField(null=True, default=None)
    due_date = models.DateField(null=True, default=None)
    price = models.PositiveIntegerField()
    format = models.CharField(
        max_length=4,
        choices=BookFormat.choices,
        default=BookFormat.Hardcover,
    )
    status = models.CharField(
        max_length=4,
        choices=BookStatus.choices,
        default=BookStatus.Available,
    )
    date_of_purchase = models.DateField()

