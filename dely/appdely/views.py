from django.shortcuts import render, get_object_or_404, redirect
from .models import Business, Review, User

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
def add_review(request, business_id):
    business = get_object_or_404(Business, id=business_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        # Usuario temporal 
        temp_user = User.objects.get(id=1)

        Review.objects.create(
            business=business,
            user=temp_user,
            rating=rating,
            comment=comment,
            reports=0  # Por defecto
        )
        return redirect('business_detail', business_id=business_id)

    return render(request, 'appdely/add_review.html', {'business': business})


