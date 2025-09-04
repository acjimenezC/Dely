from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

@csrf_exempt
@login_required
def rate_business(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            business_id = data.get('business_id')
            stars = int(data.get('stars'))
            if stars < 1 or stars > 5:
                return JsonResponse({'success': False, 'error': 'La calificación debe ser entre 1 y 5.'})
            from .models import Business, Rating
            business = Business.objects.get(id=business_id)
            rating, created = Rating.objects.get_or_create(user=request.user, business=business)
            rating.stars = stars
            rating.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})
from django.shortcuts import render, get_object_or_404, redirect
from .models import Business, Review
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

User = get_user_model()

# Lista de negocios
def business_list(request):
    businesses = Business.objects.filter(status=True)
    return render(request, 'appdely/business_list.html', {'businesses': businesses})


# Detalle de negocio con reseñas
def business_detail(request, business_id):
    business = get_object_or_404(Business, id=business_id)
    reviews = Review.objects.filter(business=business)
    return render(request, 'appdely/business_detail.html', {
        'business': business,
        'reviews': reviews
    })


# Agregar reseña
@login_required
def add_review(request, business_id):
    business = get_object_or_404(Business, id=business_id)
    user = request.user

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        Review.objects.create(
            business=business,
            user=user,
            rating=rating,
            comment=comment,
            reports=0  # Por defecto
        )
        return redirect('business_detail', business_id=business_id)

    return render(request, 'appdely/add_review.html', {'business': business})


