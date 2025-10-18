
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import models
from .forms import RegisterForm
from .forms import ProfileImageForm

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
    image_form = None
    if request.method == 'POST':
        image_form = ProfileImageForm(request.POST, request.FILES, instance=user)
        if image_form.is_valid():
            image_form.save()
            return redirect('profile')
    else:
        image_form = ProfileImageForm(instance=user)
    user_reviews = []
    total_points = 0
    try:
        from appdely.models import Review, Point
        user_reviews = Review.objects.filter(user=user).select_related('business').order_by('-date')[:10]
        # Total points: sum all movements (earn are positive, redeem are negative)
        total_points = Point.objects.filter(user=user).aggregate(total=models.Sum('amount'))['total'] or 0
        # For display, also compute earned and redeemed separately (redeemed stored as negative amounts)
        earned = Point.objects.filter(user=user, movement_type='earn').aggregate(total=models.Sum('amount'))['total'] or 0
        redeemed_sum = Point.objects.filter(user=user, movement_type='redeem').aggregate(total=models.Sum('amount'))['total'] or 0
        redeemed = abs(redeemed_sum) if redeemed_sum else 0
    except Exception:
        pass
    return render(request, 'accounts/profile.html', {
        'user': user,
        'user_reviews': user_reviews,
        'total_points': total_points,
        'earned_points': earned,
        'redeemed_points': redeemed,
        'image_form': image_form,
    })