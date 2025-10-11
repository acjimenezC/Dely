from django.urls import path
from . import views

app_name = 'appdely'

urlpatterns = [
    path('', views.business_list, name='business_list'),
    path('business/<int:business_id>/', views.business_detail, name='business_detail'),
    path('business/<int:business_id>/add_review/', views.add_review, name='add_review'),
    path('rate-business/', views.rate_business, name='rate_business'),
    path('business/<int:business_id>/discounts/', views.discounts_list, name='discounts_list'),
    path('discounts/redeem/<int:discount_id>/', views.redeem_discount, name='redeem_discount'),
    path('my_redemptions/', views.my_redemptions, name='my_redemptions'),
]