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
from django.db.models import Q
from django.db import models

User = get_user_model()

# Lista de negocios
def business_list(request):
    query = request.GET.get('q', '')
    businesses = Business.objects.filter(status=True)
    if query:
        businesses = businesses.filter(
            Q(business_name__icontains=query) | Q(description__icontains=query)
        )
    return render(request, 'appdely/business_list.html', {'businesses': businesses, 'query': query})


# Detalle de negocio con reseñas
def business_detail(request, business_id):
    business = get_object_or_404(Business, id=business_id)
    reviews = Review.objects.filter(business=business).order_by('-date')
    # Opciones de descuento (puedes ampliar)
    descuentos = [
        {'id': 1, 'title': '5% OFF', 'cost': 5},
        {'id': 2, 'title': '10% OFF', 'cost': 10},
        {'id': 3, 'title': 'Envío gratis', 'cost': 15},
    ]

    puntos = 0
    if request.user.is_authenticated:
        from appdely.models import Point
        puntos = Point.objects.filter(user=request.user).aggregate(total=models.Sum('amount'))['total'] or 0

    return render(request, 'appdely/business_detail.html', {
        'business': business,
        'reviews': reviews,
        'descuentos': descuentos,
        'puntos': puntos
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
        # Otorgar 10 puntos por crear una reseña
        try:
            from .models import Point
            Point.objects.create(
                user=user,
                amount=10,
                description='Reseña',
                movement_type='earn'
            )
        except Exception:
            # No bloquear la creación de la reseña si algo falla con puntos
            pass
        return redirect('business_detail', business_id=business_id)

    # Get recent reviews for this business
    reviews = Review.objects.filter(business=business).order_by('-id')
    return render(request, 'appdely/add_review.html', {'business': business, 'reviews': reviews})


