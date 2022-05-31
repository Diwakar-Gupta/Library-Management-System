from django.db import models


class LibraryConfig(models.Model):
    maximum_book_issue_limit = models.PositiveIntegerField(default=0, verbose_name='Issue Limit')
    maximum_day_limit = models.PositiveIntegerField(default=1, verbose_name='Max days to keep issued item')

    @classmethod
    def object(cls):
        return cls._default_manager.all().first() # Since only one item

    def save(self, *args, **kwargs):
        self.pk = self.id = 1
        return super().save(*args, **kwargs)

