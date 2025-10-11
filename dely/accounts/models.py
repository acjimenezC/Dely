from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

class UserType(models.Model):
    description = models.CharField(max_length=20)

    def __str__(self):
        return self.description


class User(AbstractUser):
    user_type = models.ForeignKey(UserType, on_delete=models.SET_NULL, null=True, blank=True)
    points_balance = models.IntegerField(default=0)

    def total_points(self):
        """Retorna el total de puntos del usuario sumando los registros en Point."""
        try:
            from django.apps import apps
            Point = apps.get_model('appdely', 'Point')
            points = Point.objects.filter(user=self).aggregate(total=models.Sum('amount'))
            return points.get('total') or 0
        except Exception:
            return 0

    @property
    def points_total(self):
        """Propiedad compatible para usar en plantillas: {{ user.points_total }}"""
        return self.total_points()
