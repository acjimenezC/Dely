from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
import logging

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
<<<<<<< Updated upstream
=======
from django.db.models import Q, Sum
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from django.conf import settings
import base64
from pathlib import Path
>>>>>>> Stashed changes

User = get_user_model()

# Lista de negocios
def business_list(request):
    businesses = Business.objects.filter(status=True)
    return render(request, 'appdely/business_list.html', {'businesses': businesses})


# Detalle de negocio con reseñas
def business_detail(request, business_id):
    business = get_object_or_404(Business, id=business_id)
    reviews = Review.objects.filter(business=business).order_by('-date')
    return render(request, 'appdely/business_detail.html', {
        'business': business,
        'reviews': reviews
    })


def discounts_list(request, business_id):
    """Muestra hasta 5 descuentos activos para un negocio."""
    business = get_object_or_404(Business, id=business_id)
    discounts = business.discounts.filter(active=True).order_by('-created_at')[:5]
    return render(request, 'appdely/discounts.html', {'business': business, 'discounts': discounts})


@login_required
def my_redemptions(request):
    """Muestra el historial de canjes del usuario (y opcionalmente el ledger de puntos)."""
    from .models import Redemption, Point
    user = request.user
    # listar redenciones más recientes primero
    redemptions = Redemption.objects.filter(user=user).select_related('discount', 'discount__business').order_by('-redeemed_at')
    # opcional: también mostrar movimientos de puntos
    points = Point.objects.filter(user=user).order_by('-registration_date')[:50]
    return render(request, 'appdely/my_redemptions.html', {'redemptions': redemptions, 'points': points})


@login_required
def redeem_discount(request, discount_id):
    """Permite al usuario redimir un descuento si tiene suficientes puntos."""
    from .models import Discount, Point, Redemption
    logger = logging.getLogger(__name__)

    discount = get_object_or_404(Discount, id=discount_id)
    user = request.user

    # Calcular puntos totales del usuario usando la misma lógica que se muestra en el perfil:
    # earned - redeemed (ambos agregados por movement_type)
    try:
        from .models import Point
        # Net sum of all movements (redeem entries are stored as negative amounts)
        total = Point.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
    except Exception:
        # fallback: usar cached balance
        total = getattr(user, 'points_balance', 0) or 0

    logger.debug("redeem_discount start: method=%s user=%s total=%s cost=%s",
                 request.method, getattr(user, 'username', None), total, getattr(discount, 'points_cost', None))

    if request.method == 'POST':
        if total >= discount.points_cost:
            logger.debug('redeem_discount: entering create block')
            try:
                with transaction.atomic():
                    # crear registro de punto negativo
                    Point.objects.create(
                        user=user,
                        amount=-discount.points_cost,
                        description=f"Canje descuento: {discount.title} en {discount.business.business_name}",
                        movement_type='redeem'
                    )
                    # actualizar balance del usuario de forma segura
                    user.points_balance = user.points_balance - discount.points_cost
                    user.save()
                    Redemption.objects.create(user=user, discount=discount)
                    logger.debug('redeem_discount: created point and redemption')
            except Exception:
                logger.exception('Error procesando canje')
                messages.error(request, 'Error al canjear el descuento. Intenta de nuevo más tarde.')
            else:
                messages.success(request, f'Descuento canjeado por {discount.points_cost} puntos.')
                # En lugar de redirigir, mostramos la página de éxito con el QR
                # Intentamos leer el PNG en static y pasar su base64 como data URI
                qr_data = None
                try:
                    static_qr = Path(settings.BASE_DIR) / 'appdely' / 'static' / 'appdely' / 'img' / 'qr_redeem.png'
                    if static_qr.exists():
                        with open(static_qr, 'rb') as f:
                            b = f.read()
                            qr_data = base64.b64encode(b).decode('ascii')
                except Exception:
                    qr_data = None

                return render(request, 'appdely/redeem_success.html', {
                    'discount': discount,
                    'points_cost': discount.points_cost,
                    'qr_data': qr_data,
                })
        else:
            messages.error(request, 'No tienes puntos suficientes para canjear este descuento.')

    return redirect('appdely:business_detail', business_id=discount.business.id)

    # Método GET muestra confirmación
    return render(request, 'appdely/redeem_confirm.html', {'discount': discount, 'total': total})


@login_required
def add_review(request, business_id):
    business = get_object_or_404(Business, id=business_id)
    user = request.user

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        # Validar rating
        try:
            rating_value = int(rating)
            if rating_value < 1 or rating_value > 5:
                messages.error(request, 'La calificación debe ser entre 1 y 5.')
                return redirect('appdely:add_review', business_id=business_id)
        except Exception:
            messages.error(request, 'Calificación inválida.')
            return redirect('appdely:add_review', business_id=business_id)

        # Crear la reseña
        review = Review.objects.create(
            business=business,
            user=user,
            rating=rating_value,
            comment=comment,
            reports=0  # Por defecto
        )

        # Otorgar puntos al usuario por crear una reseña (solo usuarios autenticados)
        # Usaremos +10 puntos por reseña; esto crea un registro Point asociada al usuario
        try:
            from .models import Point
            Point.objects.create(
                user=user,
                amount=10,
                description=f"Puntos por reseña en {business.business_name}",
                movement_type='earn'
            )
            # actualizar balance del usuario
            user.points_balance = user.points_balance + 10
            user.save()
        except Exception:
            # No interrumpimos la creación de la reseña si falla el registro de puntos
            pass

        messages.success(request, 'Reseña enviada y puntos otorgados.')
        return redirect('appdely:business_detail', business_id=business_id)

    # Si es GET, mostrar el formulario de agregar reseña
    reviews = Review.objects.filter(business=business).order_by('-id')
    return render(request, 'appdely/add_review.html', {'business': business, 'reviews': reviews})


