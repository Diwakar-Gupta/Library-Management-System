from django.db import models


class Notification(models.Model):
    created_on = models.DateField()
    content = models.TextField()


class EmailNotification(models.Model):
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE)
    email = models.EmailField()
    send_on = models.DateTimeField(null=True)
    
    def sendNotification(self):
        # TODO
        return None

