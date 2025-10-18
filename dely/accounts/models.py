from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

class UserType(models.Model):
    description = models.CharField(max_length=20)

    def __str__(self):
        return self.description


class User(AbstractUser):
    user_type = models.ForeignKey(UserType, on_delete=models.SET_NULL, null=True, blank=True)
    # optional profile image stored in MEDIA_ROOT/profiles/
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    # Profile image for the user. Optional; stored in MEDIA_ROOT/profiles/
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
