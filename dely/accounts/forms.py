from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email or '@' not in email:
            raise ValidationError('Introduce un email válido.')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Ya existe un usuario con este email.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('El nombre de usuario ya está en uso.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if not password1 or not password2:
            raise ValidationError('Debes completar ambos campos de contraseña.')
        if password1 != password2:
            raise ValidationError('Las contraseñas no coinciden.')
        try:
            validate_password(password1)
        except ValidationError as e:
            self.add_error('password1', e)
        return cleaned_data
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email or '@' not in email:
            raise ValidationError('Introduce un email válido.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if not password1 or not password2:
            raise ValidationError('Debes completar ambos campos de contraseña.')
        if password1 != password2:
            raise ValidationError('Las contraseñas no coinciden.')
        return cleaned_data