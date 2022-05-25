from django.db import models


class ReservationStatus(models.TextChoices):
        Waiting = 'W', ('Waiting')
        Pending = 'P', ('Pending')
        Completed = 'COM', ('Completed')
        Canceled = 'CAN', ('Canceled')

class BookReservation(models.Model):
    creation_date = models.DateField()
    status = models.CharField(
        max_length=4,
        choices=ReservationStatus.choices,
        default=ReservationStatus.Waiting,
    )

    def get_status(self):
        # TODO
        return None

    def fetch_reservation_details(self):
        # TODO
        return None


class BookLending(models.Model):
    creation_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(blank=True)
    
    def get_return_date(self):
        # TODO
        return None