from django.db import models
from lms.models import BookLending


class Fine(models.Model):
    amount = models.PositiveIntegerField()
    lending = models.ForeignKey(BookLending, on_delete=models.CASCADE)

    def get_amount(self):
        return self.amount


class FineTransaction(models.Model):
    fine = models.ForeignKey(Fine, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(null=True)
    amount = models.PositiveIntegerField()


class CashTransaction(models.Model):
    transaction = models.OneToOneField(FineTransaction, on_delete=models.CASCADE)

