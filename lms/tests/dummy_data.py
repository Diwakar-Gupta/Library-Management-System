from datetime import datetime
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from lms.models import BookItem, BookLending, LibraryConfig
from lms.models.action import BookReservation
from lms.models.book import Book, Rack
from lms.models.account import Account, AccountStatus

class DummyDataMixin(object):
    
    @classmethod
    def setUpTestData(cls):

        def create_librarian_group():
            librarian, _ = Group.objects.get_or_create(name='Librarian')
            book_item = ContentType.objects.get_for_model(BookItem)
            book_lending = ContentType.objects.get_for_model(BookLending)
            book_reservation = ContentType.objects.get_for_model(BookReservation)

            librarian_permissions = [
                ('can_checkout_book_item', 'Can CheckOut Book Item', book_item),
                ('can_issue_book_item', 'Can Give Book Item', book_item),
                ('can_reserve_for_others', "Can Reserve Book Item for other's", book_reservation),
                ('change_bookreservation', 'Can change book reservation', book_reservation),
                ('view_bookreservation', 'Can view book reservation', book_reservation),
                ('view_booklending', 'Can view book lending', book_lending),
            ]
            for codename, name, content_type in librarian_permissions:
                permission, _ = Permission.objects.get_or_create(
                                    codename=codename,
                                    content_type=content_type)
                librarian.permissions.add(permission)
            return librarian

        _ = create_librarian_group()

        obj, created = LibraryConfig.objects.get_or_create(pk=1)
        if created:
            obj.maximum_book_issue_limit = 3
            obj.maximum_day_limit = 10
            obj.fine_per_late_day = 10
            obj.save()

        librarian = Group.objects.get(name='Librarian')

        raju, _ = User.objects.get_or_create(username='librarian', first_name='Raju')
        raju.set_password('Raju')
        raju.save()
        librarian.user_set.add(raju)
        Account.objects.create(id=20, user=raju, status=AccountStatus.Active, phone_number='+91898989899')

        abrar, _ = User.objects.get_or_create(username='abrar', first_name='Abrar')
        abrar.set_password('abrar')
        abrar.save()
        Account.objects.create(id=30,user=abrar, status=AccountStatus.Active, phone_number='+91898989899').save()

        atul, _ = User.objects.get_or_create(username='atul', first_name='Atul')
        atul.set_password('atul')
        atul.save()
        Account.objects.create(id=40, user=atul, status=AccountStatus.Active, phone_number='+91898989899')

        diwakar, _ = User.objects.get_or_create(username='diwakar', first_name='Diwakar')
        diwakar.set_password('diwakar')
        diwakar.save()
        Account.objects.create(id=50, user=diwakar, phone_number='+91898989899')

        book1 = Book.objects.create(isbn='453678754', title='Hands on machine learining', subject='Data Science', publisher='Oreally', language='Englist', numer_of_pages=899)
        
        BookItem.objects.create(book=book1, barcode='barcode123', is_reference_only=False, price=100, date_of_purchase=datetime.now().date(), placed_at=Rack.objects.create(number=9, location_identifier='RL'))
        BookItem.objects.create(book=book1, barcode='barcode123-1', is_reference_only=True, price=100, date_of_purchase=datetime.now().date(), placed_at=Rack.objects.create(number=9, location_identifier='RQ'))
