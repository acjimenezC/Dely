
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterForm

def register(request):
    from django.contrib import messages
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido a Dely.')
            return redirect('/')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})