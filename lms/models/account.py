from django.db import models
from django.utils.functional import cached_property
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class AccountStatus(models.TextChoices):
        Active = 'AC', ('Active')
        Closed = 'CL', ('Closed')
        Canceled = 'CN', ('Canceled')
        Blacklisted = 'BL', ('Blacklisted')
        

class Account(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    status = models.CharField(
        max_length=2,
        choices=AccountStatus.choices,
        blank=True
    )
    issued_book_count = models.PositiveIntegerField(default=0)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) # Validators should be a list

    def __str__(self):
        return self.user.username
    
    def get_name(self):
        return self.user.get_full_name()
    
    def get_email(self):
        return self.user.email

    @cached_property
    def is_librarian(user):
        return user.groups.filter(name='Librarian').exists()

    @classmethod
    def can_return(cls, user):
        return user.has_perm('lms.can_return_book_item')
    
    @classmethod
    def can_checkout(cls, user):
        return user.has_perm('lms.can_checkout_book_item')
    
    def can_see_lending(self, lending):
        if self.user.has_perm('lms.view_booklending'):
            return True
        else:
            return lending.account == self
    
    @classmethod
    def can_see_all_lendings(cls, user):
        return user.has_perm('lms.view_booklending')
    
    def is_active(self):
        return self.status == AccountStatus.Active

    def remaining_issue_count(self):
        from lms.models import LibraryConfig
        
        return LibraryConfig.object().maximum_book_issue_limit - self.issued_book_count

    def recalculate_issued_book_count(self):
        from lms.models.action import BookLending

        self.issued_book_count = BookLending.objects.filter(account=self, return_date=None).count()
        self.save()
        return self.issued_book_count
