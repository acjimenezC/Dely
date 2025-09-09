
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import models
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

@login_required
def profile(request):
    user = request.user
    user_reviews = []
    total_points = 0
    try:
        from appdely.models import Review, Point
        user_reviews = Review.objects.filter(user=user).select_related('business').order_by('-date')[:10]
        earned = Point.objects.filter(user=user, movement_type='earn').aggregate(models.Sum('amount'))['amount__sum'] or 0
        redeemed = Point.objects.filter(user=user, movement_type='redeem').aggregate(models.Sum('amount'))['amount__sum'] or 0
        total_points = earned - redeemed
    except Exception:
        pass
    return render(request, 'accounts/profile.html', {
        'user': user,
        'user_reviews': user_reviews,
        'total_points': total_points
    })