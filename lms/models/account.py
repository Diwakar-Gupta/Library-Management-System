from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class AccountStatus(models.TextChoices):
        Active = 'AC', ('Active')
        Closed = 'CL', ('Closed')
        Canceled = 'CN', ('Canceled')
        Blacklisted = 'BL', ('Blacklisted')
        

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    status = models.CharField(
        max_length=2,
        choices=AccountStatus.choices,
        blank=True
    )
    email = models.EmailField()
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) # Validators should be a list

    def __str__(self):
        return self.user.username
