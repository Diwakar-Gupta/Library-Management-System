from django.contrib import admin

# Register your models here.
from lms.models import Book, BookItem

admin.site.register(Book)
admin.site.register(BookItem)