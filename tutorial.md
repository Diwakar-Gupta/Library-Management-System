https://www.educative.io/courses/grokking-the-object-oriented-design-interview/RMlM3NgjAyR#Use-case-diagram

Create necessary objects
```
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from lms.models import BookItem

librarian, _ = Group.objects.get_or_create(name='librarian')

book_item = ContentType.objects.get_for_model(BookItem)

librarian_permissions = [
    ('can_checkout_book_item', 'Can CheckOut Book Item', book_item),
    ('can_checkin_book_item', 'Can CheckIn Book Item', book_item),
    ('can_checkout_book_item', 'Can CheckOut Book Item', book_item),
]

# Now what - Say I want to add 'Can add project' permission to new_group?
for codename, name, content_type in librarian_permissions:
    permission, _ = Permission.objects.get_or_create(
                        codename=codename,
                        name=name,
                        content_type=content_type)
    librarian.permissions.add(permission)
```
