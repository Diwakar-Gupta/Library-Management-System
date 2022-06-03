from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from lms.models import BookItem, BookLending, LibraryConfig

def create_librarian_group():
    librarian, _ = Group.objects.get_or_create(name='Librarian')
    book_item = ContentType.objects.get_for_model(BookItem)
    book_lending = ContentType.objects.get_for_model(BookLending)
    librarian_permissions = [
        ('can_checkout_book_item', 'Can CheckOut Book Item', book_item),
        ('can_issue_book_item', 'Can Give Book Item', book_item),
    ]
    for codename, name, content_type in librarian_permissions:
        permission, _ = Permission.objects.get_or_create(
                            codename=codename,
                            name=name,
                            content_type=content_type)
        librarian.permissions.add(permission)
    view_booklending = Permission.objects.get(codename='view_booklending')
    librarian.permissions.add(view_booklending)
    return librarian

_ = create_librarian_group()

obj, created = LibraryConfig.objects.get_or_create(pk=1)
if created:
    obj.maximum_book_issue_limit = 3
    obj.maximum_day_limit = 10
    obj.fine_per_late_day = 10
    obj.save()
