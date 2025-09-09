from django.contrib import admin
from django.contrib import admin

from .models import  BusinessType, Business, BusinessImage, Favorite, Review, Point

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
	list_display = ('business_name', 'average_rating')

admin.site.register(BusinessType)
admin.site.register(Favorite)
admin.site.register(Review)
admin.site.register(Point)
admin.site.register(BusinessImage)
