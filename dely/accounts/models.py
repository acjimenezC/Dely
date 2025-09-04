from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

class UserType(models.Model):
    description = models.CharField(max_length=20)

    def __str__(self):
        return self.description


class User(AbstractUser):
    user_type = models.ForeignKey(UserType, on_delete=models.SET_NULL, null=True, blank=True)
