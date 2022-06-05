from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from lms.models import BookItem, BookLending


librarian = Group.objects.get(name='Librarian')

raju, _ = User.objects.get_or_create(username='librarian', first_name='Raju')
raju.set_password('Raju')
raju.save()
librarian.user_set.add(raju)

abrar, _ = User.objects.get_or_create(username='abrar', first_name='Abrar')
abrar.set_password('abrar')
abrar.save()

atul, _ = User.objects.get_or_create(username='atul', first_name='Atul')
atul.set_password('atul')
atul.save()

