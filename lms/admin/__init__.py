from django.contrib import admin

from lms.models import Book, BookItem, Rack, Account, BookReservation, BookLending, Notification, EmailNotification, Fine
from lms.models import LibraryConfig
from .account import AccountAdmin
from .book import BookItemAdmin
from .lending import BookLendingAdmin
from .notification import NotificationAdmin


admin.site.register(Book)
admin.site.register(Rack)
admin.site.register(BookReservation)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(EmailNotification)
admin.site.register(Fine)
admin.site.register(LibraryConfig)
admin.site.register(BookLending, BookLendingAdmin)
admin.site.register(BookItem, BookItemAdmin)
admin.site.register(Account, AccountAdmin)

