from django.contrib import admin

# Register your models here.
from lms.models import Book, BookItem, Rack, Account, BookReservation, BookLending, Notification, EmailNotification, Fine
from lms.models import LibraryConfig
from .account import AccountAdmin
from .book import BookItemAdmin

admin.site.register(Book)
admin.site.register(Rack)
admin.site.register(BookReservation)
admin.site.register(BookLending)
admin.site.register(Notification)
admin.site.register(EmailNotification)
admin.site.register(Fine)
admin.site.register(LibraryConfig)
admin.site.register(BookItem, BookItemAdmin)
admin.site.register(Account, AccountAdmin)