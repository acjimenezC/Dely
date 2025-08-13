from django.urls import path
from . import views

urlpatterns = [
    path('', views.business_list, name='business_list'),
    path('business/<int:business_id>/', views.business_detail, name='business_detail'),
    path('business/<int:business_id>/add_review/', views.add_review, name='add_review'),
]