from django.urls import path 
from . import views 

urlpatterns = [
    # Promociones
    path('', views.promociones_list, name='promociones_list'),
    path('promocion/<int:pk>/', views.promocion_detail, name='promocion_detail'),
    
    # Noticias
    path('noticias/', views.noticias_list, name='noticias_list'),
    path('noticia/<int:pk>/', views.noticia_detail, name='noticia_detail'),
    
    # Vista combinada (promociones + noticias)
    path('todas/', views.promociones_noticias, name='promociones_noticias'),
    path('subscribe/', views.subscribe, name='promociones_subscribe'),
    path('register-business/', views.register_business, name='promociones_register_business'),
    # Descuentos
    path('descuentos/', views.descuentos_list, name='descuentos_list'),
    path('descuentos/<int:opcion_id>/qr/', views.descuento_qr, name='descuento_qr'),
    path('historial/', views.historial_canje, name='historial_canje'),
]
