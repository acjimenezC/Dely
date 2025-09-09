from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/accounts/logout-success/'), name='logout'),
    path('logout-success/', auth_views.TemplateView.as_view(template_name='accounts/logout_success.html'), name='logout_success'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
]