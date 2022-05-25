from django.contrib import admin

# Register your models here.
from lms.models import Book, BookItem, Rack, Account, BookReservation, BookLending, Notification, EmailNotification, Fine

admin.site.register(Book)
admin.site.register(BookItem)
admin.site.register(Rack)
admin.site.register(Account)
admin.site.register(BookReservation)
admin.site.register(BookLending)
admin.site.register(Notification)
admin.site.register(EmailNotification)
admin.site.register(Fine)

