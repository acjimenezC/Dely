
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
    # handle profile image upload
    profile = getattr(user, 'profile', None)
    if request.method == 'POST':
        # handle delete first
        if request.POST.get('remove_image') and profile and profile.image:
            try:
                # remove file from storage
                profile.image.delete(save=False)
            except Exception:
                pass
            profile.image = None
            profile.save()
            return redirect('profile')

        form = ProfileImageForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileImageForm(instance=profile)

    return render(request, 'accounts/profile.html', {
        'user': user,
        'user_reviews': user_reviews,
        'total_points': total_points,
        'profile': profile,
        'form': form,
    })