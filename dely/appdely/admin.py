from django.contrib import admin
from django.contrib import admin
from .models import  BusinessType, Business, BusinessImage, Favorite, Review, Point

admin.site.register(BusinessType)
admin.site.register(Business)
admin.site.register(Favorite)
admin.site.register(Review)
admin.site.register(Point)
admin.site.register(BusinessImage)
