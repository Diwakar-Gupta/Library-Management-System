from django.db import models
from django.forms import ValidationError


class LibraryConfig(models.Model):
    maximum_book_issue_limit = models.PositiveIntegerField(default=0, verbose_name='Issue Limit')
    maximum_day_limit = models.PositiveIntegerField(default=1, verbose_name='Max days to keep issued item')
    fine_per_late_day = models.PositiveSmallIntegerField(default=10)

    @classmethod
    def object(cls):
        obj, _ = cls.objects.get_or_create(pk=1) # Since only one item
        return obj

    def clean(self, *args, **kwargs):
        if hasattr(self, 'pk'):
            if self.pk != 1:
                raise ValidationError('Only one instance allowed')
        
        return super(LibraryConfig, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        if hasattr(self, 'pk'):
            assert self.pk == 1, "Only one instance allowed"
            return super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        if self.pk == 1:
            pass
        else:
            return super(LibraryConfig, self).delete(self, *args, **kwargs)

