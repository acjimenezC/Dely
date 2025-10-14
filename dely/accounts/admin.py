from django.contrib import admin
from .models import User, UserType
from .models import Profile

admin.site.register(User)
admin.site.register(UserType)
admin.site.register(Profile)
