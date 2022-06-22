from django.db import models
from lms.models import Account


class Notification(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, db_index=True)
    created_on = models.DateField(auto_now_add=True, db_index=True)
    content = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)


class EmailNotification(models.Model):
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE)
    email = models.EmailField()
    send_on = models.DateTimeField(null=True)
    
    def sendNotification(self):
        # TODO
        return None

