from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Promocion, NoticiaRestaurante, TipoPromocion
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from appdely.models import Point
from django.contrib import messages
from django.db import models
from django.templatetags.static import static


def promociones_list(request):
    """Lista todas las promociones activas"""
    # Filtrar solo promociones activas
    promociones = Promocion.objects.filter(activa=True).select_related('restaurante', 'tipo_promocion')
    
    # Filtro por tipo de promoción
    tipo_filtro = request.GET.get('tipo')
    if tipo_filtro:
        promociones = promociones.filter(tipo_promocion__id=tipo_filtro)
    
    # Filtro por restaurante
    restaurante_filtro = request.GET.get('restaurante')
    if restaurante_filtro:
        promociones = promociones.filter(restaurante__business_name__icontains=restaurante_filtro)
    
    # Ordenar por fecha de creación
    promociones = promociones.order_by('-creada_en')
    
    # Paginación
    paginator = Paginator(promociones, 12)  # 12 promociones por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener tipos de promoción para el filtro
    tipos_promocion = TipoPromocion.objects.all()
    
    context = {
        'promociones': page_obj,
        'tipos_promocion': tipos_promocion,
        'tipo_seleccionado': tipo_filtro,
        'restaurante_busqueda': restaurante_filtro,
    }
    
    return render(request, 'promociones/promociones_list.html', context)


def promocion_detail(request, pk):
    """Detalle de una promoción específica"""
    promocion = get_object_or_404(Promocion, pk=pk)
    
    # Incrementar contador de vistas
    promocion.incrementar_vistas()
    
    # Obtener promociones relacionadas del mismo restaurante
    promociones_relacionadas = Promocion.objects.filter(
        restaurante=promocion.restaurante,
        activa=True
    ).exclude(pk=pk)[:3]
    
    context = {
        'promocion': promocion,
        'promociones_relacionadas': promociones_relacionadas,
        'esta_activa': promocion.esta_activa(),
        'tiempo_restante': promocion.tiempo_restante(),
        'descuento_calculado': promocion.calcular_descuento(),
    }
    
    return render(request, 'promociones/promocion_detail.html', context)


def noticias_list(request):
    """Lista todas las noticias de restaurantes"""
    noticias = NoticiaRestaurante.objects.filter(activa=True).select_related('restaurante', 'autor')
    
    # Filtro por tipo de noticia
    tipo_filtro = request.GET.get('tipo')
    if tipo_filtro:
        noticias = noticias.filter(tipo_noticia=tipo_filtro)
    
    # Filtro por restaurante
    restaurante_filtro = request.GET.get('restaurante')
    if restaurante_filtro:
        noticias = noticias.filter(restaurante__business_name__icontains=restaurante_filtro)
    
    # Búsqueda por título
    busqueda = request.GET.get('q')
    if busqueda:
        noticias = noticias.filter(
            Q(titulo__icontains=busqueda) | 
            Q(contenido__icontains=busqueda) |
            Q(resumen__icontains=busqueda)
        )
    
    # Ordenar por fecha de publicación
    noticias = noticias.order_by('-fecha_publicacion')
    
    # Paginación
    paginator = Paginator(noticias, 10)  # 10 noticias por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Noticias destacadas para el banner
    noticias_destacadas = NoticiaRestaurante.objects.filter(
        activa=True, 
        destacada=True
    ).order_by('-fecha_publicacion')[:3]
    
    # Tipos de noticia para el filtro
    tipos_noticia = NoticiaRestaurante.TIPO_NOTICIA_CHOICES
    
    context = {
        'noticias': page_obj,
        'noticias_destacadas': noticias_destacadas,
        'tipos_noticia': tipos_noticia,
        'tipo_seleccionado': tipo_filtro,
        'restaurante_busqueda': restaurante_filtro,
        'busqueda': busqueda,
    }
    
    return render(request, 'promociones/noticias_list.html', context)


def noticia_detail(request, pk):
    """Detalle de una noticia específica"""
    noticia = get_object_or_404(NoticiaRestaurante, pk=pk, activa=True)
    
    # Incrementar contador de vistas
    noticia.incrementar_vistas()
    
    # Obtener noticias relacionadas
    noticias_relacionadas = NoticiaRestaurante.objects.filter(
        activa=True,
        tipo_noticia=noticia.tipo_noticia
    ).exclude(pk=pk).order_by('-fecha_publicacion')[:4]
    
    # Si la noticia está asociada a un restaurante, obtener sus promociones
    promociones_restaurante = []
    if noticia.restaurante:
        promociones_restaurante = Promocion.objects.filter(
            restaurante=noticia.restaurante,
            activa=True
        )[:3]
    
    context = {
        'noticia': noticia,
        'noticias_relacionadas': noticias_relacionadas,
        'promociones_restaurante': promociones_restaurante,
        'galeria_imagenes': noticia.obtener_galeria(),
    }
    
    return render(request, 'promociones/noticia_detail.html', context)


def promociones_noticias(request):
    """Vista combinada: promociones destacadas + noticias recientes"""
    # Promociones destacadas (las más vistas o recientes)
    promociones_destacadas = Promocion.objects.filter(
        activa=True
    ).order_by('-vistas', '-creada_en')[:6]
    
    # Noticias recientes
    noticias_recientes = NoticiaRestaurante.objects.filter(
        activa=True
    ).order_by('-fecha_publicacion')[:8]
    
    # Promociones que terminan pronto (urgentes)
    hoy = timezone.now().date()
    promociones_urgentes = Promocion.objects.filter(
        activa=True,
        fecha_fin__gte=hoy,
        fecha_fin__lte=hoy + timezone.timedelta(days=3)
    ).order_by('fecha_fin')[:4]
    
    # Estadísticas generales
    total_promociones_activas = Promocion.objects.filter(activa=True).count()
    total_noticias = NoticiaRestaurante.objects.filter(activa=True).count()
    
    context = {
        'promociones_destacadas': promociones_destacadas,
        'noticias_recientes': noticias_recientes,
        'promociones_urgentes': promociones_urgentes,
        'total_promociones_activas': total_promociones_activas,
        'total_noticias': total_noticias,
    }
    
    return render(request, 'promociones/promociones_noticias.html', context)


@login_required
def descuentos_list(request):
    """Muestra opciones de descuento que el usuario puede redimir."""
    # Opciones estáticas (2-3). Pueden ampliarse a modelos si se desea.
    opciones = [
        {'id': 1, 'title': '5% OFF - Código A', 'cost': 5},
        {'id': 2, 'title': '10% OFF - Código B', 'cost': 10},
        {'id': 3, 'title': 'Envío gratis - Código C', 'cost': 15},
    ]

    # Calcular puntos acumulados del usuario
    puntos = Point.objects.filter(user=request.user).aggregate(total=models.Sum('amount'))['total'] or 0

    return render(request, 'promociones/descuentos_list.html', {'opciones': opciones, 'puntos': puntos})


@login_required
def descuento_qr(request, opcion_id):
    """Redime un descuento (resta 5 puntos) y muestra el QR si hay suficientes puntos."""
    try:
        opcion_id = int(opcion_id)
    except Exception:
        messages.error(request, 'Opción inválida.')
        return redirect('promociones_list')

    # Verificar puntos
    puntos = Point.objects.filter(user=request.user).aggregate(total=models.Sum('amount'))['total'] or 0
    # Buscar la opción y su coste
    opciones_map = {o['id']: o for o in [
        {'id': 1, 'title': '5% OFF - Código A', 'cost': 5},
        {'id': 2, 'title': '10% OFF - Código B', 'cost': 10},
        {'id': 3, 'title': 'Envío gratis - Código C', 'cost': 15},
    ]}

    opcion = opciones_map.get(opcion_id)
    if not opcion:
        messages.error(request, 'Opción de descuento no encontrada.')
        return redirect('descuentos_list')

    cost = opcion['cost']
    if puntos < cost:
        messages.error(request, 'No tienes suficientes puntos para redimir este descuento.')
        return redirect('descuentos_list')

    # Registrar movimiento de -cost puntos
    Point.objects.create(
        user=request.user,
        amount=-cost,
        description=f'Redención descuento opción {opcion_id} ({opcion["title"]})',
        movement_type='redeem'
    )

    # Mostrar plantilla con el QR (el QR debe colocarse en static/promociones/img/qr.png o ruta similar)
    # Construimos la URL estática con la utilidad de Django para evitar problemas de ruta
    qr_url = static('promociones/img/qr.png')
    return render(request, 'promociones/descuento_qr.html', {'qr_url': qr_url})


@login_required
def historial_canje(request):
    """Muestra el historial de redenciones del usuario"""
    try:
        redenciones = Point.objects.filter(user=request.user, movement_type='redeem').order_by('-registration_date')
    except Exception:
        redenciones = []
    return render(request, 'promociones/historial_canje.html', {'redenciones': redenciones})

