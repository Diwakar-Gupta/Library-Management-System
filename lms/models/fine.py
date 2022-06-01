from django.db import models
from lms.models import BookLending


class Fine(models.Model):
    amount = models.PositiveIntegerField()
    lending = models.OneToOneField(BookLending, on_delete=models.CASCADE)

    def get_amount(self):
        return self.amount


class FineTransaction(models.Model):
    creation_date = models.DateTimeField()
    amount = models.PositiveIntegerField()


class CashTransaction(models.Model):
    transaction = models.OneToOneField(FineTransaction, on_delete=models.CASCADE)

