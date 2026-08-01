from django.db import models
from django.conf import settings

class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        update_kwargs = {'is_deleted': True}
        field_names = [f.name for f in self.model._meta.get_fields()]
        if 'is_active' in field_names:
            update_kwargs['is_active'] = False
        return self.update(**update_kwargs)

    def hard_delete(self):
        return super().delete()
    
    def restore(self):
        update_kwargs = {'is_deleted': False}
        field_names = [f.name for f in self.model._meta.get_fields()]
        if 'is_active' in field_names:
            update_kwargs['is_active'] = True
        return self.update(**update_kwargs)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_created",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_updated",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_deleted = models.BooleanField(default=False, db_index=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def _has_is_active(self):
        return hasattr(self, 'is_active') and 'is_active' in [
            f.name for f in self._meta.get_fields()
        ]

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        if self._has_is_active():
            self.is_active = False
        self.save()

    def restore(self):
        self.is_deleted = False
        if self._has_is_active():
            self.is_active = True
        self.save()