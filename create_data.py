from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from lms.models import BookItem, BookLending

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

librarian = create_librarian_group()

raju, _ = User.objects.get_or_create(username='librarianRaju', first_name='Raju')
raju.set_password('Raju')
raju.save()

abrar, _ = User.objects.get_or_create(username='abrar', first_name='Abrar')
abrar.set_password('abrar')
abrar.save()

atul, _ = User.objects.get_or_create(username='atul', first_name='Atul')
atul.set_password('atul')
atul.save()

librarian.user_set.add(raju)

