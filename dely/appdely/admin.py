from django.contrib import admin

from django.contrib import admin
from .models import UserType, User, BusinessType, Business, Favorite, Review, Point, BusinessImage

admin.site.register(UserType)
admin.site.register(User)
admin.site.register(BusinessType)
admin.site.register(Business)
admin.site.register(Favorite)
admin.site.register(Review)
admin.site.register(Point)
admin.site.register(BusinessImage)
