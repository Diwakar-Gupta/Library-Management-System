from django.db import models
from django.utils.functional import cached_property


class LibraryConfig(models.Model):
    maximum_book_issue_limit = models.PositiveIntegerField(default=0, verbose_name='Issue Limit')
    maximum_day_limit = models.PositiveIntegerField(default=1, verbose_name='Max days to keep issued item')
    fine_per_late_day = models.PositiveSmallIntegerField(default=10)

    @classmethod
    @cached_property
    def object(cls):
        return cls._default_manager.all().first() # Since only one item

    def save(self, *args, **kwargs):
        if self.pk != LibraryConfig.object.pk:
            return
        return super().save(*args, **kwargs)

