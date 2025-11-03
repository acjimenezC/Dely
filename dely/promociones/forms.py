from django import forms
from .models import Subscriber, BusinessRegistration


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']
        labels = {
            'email': 'Correo Electrónico',
        }
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@correo.com',
            }),
        }


class BusinessRegistrationForm(forms.ModelForm):
    class Meta:
        model = BusinessRegistration
        fields = ['business_name', 'contact_name', 'contact_email', 'phone', 'address', 'description']
        labels = {
            'business_name': 'Nombre del Negocio',
            'contact_name': 'Nombre de Contacto',
            'contact_email': 'Correo de Contacto',
            'phone': 'Teléfono',
            'address': 'Dirección',
            'description': 'Descripción del Negocio',
        }
        widgets = {
            'business_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: La Parrilla Deliciosa',
            }),
            'contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu nombre completo',
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@correo.com',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+(57) 300 1234567',
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Calle 10 # 5-50, Medellín',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Cuéntanos sobre tu negocio, tipo de comida, especialidades, etc...',
            }),
        }
