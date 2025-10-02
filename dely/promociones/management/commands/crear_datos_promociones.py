from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from promociones.models import TipoPromocion, Promocion, NoticiaRestaurante
from appdely.models import Business
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Crear datos de ejemplo para promociones y noticias'

    def handle(self, *args, **options):
        self.stdout.write("Creando datos de ejemplo...")

        # Crear tipos de promoción
        tipos = [
            {'nombre': 'Descuento', 'descripcion': 'Descuentos en porcentaje'},
            {'nombre': '2x1', 'descripcion': 'Dos por el precio de uno'},
            {'nombre': 'Combo', 'descripcion': 'Ofertas de combos especiales'},
            {'nombre': 'Happy Hour', 'descripcion': 'Ofertas de hora feliz'},
            {'nombre': 'Evento Especial', 'descripcion': 'Promociones para eventos especiales'},
        ]

        for tipo_data in tipos:
            tipo, created = TipoPromocion.objects.get_or_create(**tipo_data)
            if created:
                self.stdout.write(f"✓ Creado tipo: {tipo.nombre}")

        # Obtener algunos restaurantes
        restaurantes = Business.objects.all()[:5]
        if not restaurantes:
            self.stdout.write(self.style.WARNING("No hay restaurantes disponibles. Crea algunos primero."))
            return

        # Obtener usuario admin
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.first()
        except:
            admin_user = None

        # Crear promociones de ejemplo
        promociones_data = [
            {
                'titulo': '🍔 Combo Burger Especial',
                'descripcion': 'Deliciosa hamburguesa artesanal con papas fritas y bebida. Ingredientes frescos y pan casero.',
                'descripcion_corta': 'Hamburguesa + papas + bebida',
                'descuento_porcentaje': 25.00,
                'precio_original': 35000,
                'precio_promocional': 26250,
                'fecha_inicio': timezone.now().date(),
                'fecha_fin': timezone.now().date() + timedelta(days=30),
                'imagen_principal': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&h=300&fit=crop',
                'terminos_condiciones': 'Válido de lunes a viernes. No acumulable con otras promociones.'
            },
            {
                'titulo': '🍕 2x1 en Pizzas Familiares',
                'descripcion': 'Llévate dos pizzas familiares por el precio de una. Perfectas para compartir en familia.',
                'descripcion_corta': 'Dos pizzas familiares por el precio de una',
                'descuento_porcentaje': 50.00,
                'precio_original': 45000,
                'precio_promocional': 45000,
                'fecha_inicio': timezone.now().date(),
                'fecha_fin': timezone.now().date() + timedelta(days=15),
                'imagen_principal': 'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400&h=300&fit=crop',
                'terminos_condiciones': 'Válido todos los días. Aplica para pizzas de igual o menor valor.'
            },
            {
                'titulo': '🍺 Happy Hour - 50% en Bebidas',
                'descripcion': 'Disfruta de nuestro happy hour con 50% de descuento en todas las bebidas alcohólicas.',
                'descripcion_corta': '50% descuento en bebidas alcohólicas',
                'descuento_porcentaje': 50.00,
                'fecha_inicio': timezone.now().date(),
                'fecha_fin': timezone.now().date() + timedelta(days=60),
                'hora_inicio': '17:00',
                'hora_fin': '19:00',
                'imagen_principal': 'https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=400&h=300&fit=crop',
                'terminos_condiciones': 'Solo de 5:00 PM a 7:00 PM. No aplica en días festivos.'
            },
            {
                'titulo': '🥗 Menú Saludable - Almuerzo Ejecutivo',
                'descripcion': 'Almuerzo ejecutivo con opciones saludables. Incluye entrada, plato principal y postre.',
                'descripcion_corta': 'Almuerzo ejecutivo completo',
                'precio_original': 28000,
                'precio_promocional': 22000,
                'fecha_inicio': timezone.now().date(),
                'fecha_fin': timezone.now().date() + timedelta(days=45),
                'hora_inicio': '12:00',
                'hora_fin': '15:00',
                'imagen_principal': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop',
                'dias_validos': '12345'  # Lunes a viernes
            },
            {
                'titulo': '🎂 Postre Gratis en tu Cumpleaños',
                'descripcion': 'Celebra tu cumpleaños con nosotros y obtén un postre completamente gratis.',
                'descripcion_corta': 'Postre gratis el día de tu cumpleaños',
                'descuento_porcentaje': 100.00,
                'fecha_inicio': timezone.now().date(),
                'fecha_fin': timezone.now().date() + timedelta(days=365),
                'imagen_principal': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&h=300&fit=crop',
                'terminos_condiciones': 'Válido el día del cumpleaños. Presentar documento de identidad.'
            }
        ]

        tipos_obj = list(TipoPromocion.objects.all())
        
        for i, promo_data in enumerate(promociones_data):
            restaurante = restaurantes[i % len(restaurantes)]
            tipo = tipos_obj[i % len(tipos_obj)]
            
            promo_data['restaurante'] = restaurante
            promo_data['tipo_promocion'] = tipo
            if admin_user:
                promo_data['creada_por'] = admin_user
            
            promocion, created = Promocion.objects.get_or_create(
                titulo=promo_data['titulo'],
                defaults=promo_data
            )
            if created:
                self.stdout.write(f"✓ Creada promoción: {promocion.titulo}")

        # Crear noticias de ejemplo
        noticias_data = [
            {
                'titulo': '🍽️ Nueva Carta de Temporada Disponible',
                'subtitulo': 'Descubre sabores únicos con ingredientes frescos de temporada',
                'contenido': '''Estamos emocionados de presentar nuestra nueva carta de temporada, diseñada especialmente para destacar los sabores frescos y auténticos de los ingredientes locales.

Nuestro chef ha trabajado durante semanas para crear platos únicos que combinan técnicas tradicionales con toques modernos. Cada plato ha sido cuidadosamente elaborado para ofrecerte una experiencia gastronómica inolvidable.

Algunos destacados de nuestra nueva carta:
- Ceviche de pescado fresco con maracuyá
- Risotto de quinoa con vegetales de temporada  
- Tacos de pollo adobado con salsa de aguacate
- Brownie de chocolate con helado artesanal

Ven y descubre estos nuevos sabores que te sorprenderán.''',
                'resumen': 'Nueva carta de temporada con ingredientes frescos y sabores únicos.',
                'tipo_noticia': 'nuevo_plato',
                'imagen_destacada': 'https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=600&h=400&fit=crop',
                'destacada': True
            },
            {
                'titulo': '👨‍🍳 Chef Invitado: Una Noche de Gastronomía Internacional',
                'contenido': '''El próximo viernes tendremos la visita del reconocido chef internacional Marco Antonelli, quien preparará un menú especial de 5 tiempos.

Esta es una oportunidad única de disfrutar de alta cocina italiana en nuestra ciudad. El chef Marco ha trabajado en restaurantes Michelin en Roma y Milán.

El menú incluye:
1. Antipasto della casa
2. Pasta fresca con trufa negra
3. Osso buco alla milanese
4. Selección de quesos italianos
5. Tiramisú tradicional

Reservas limitadas. ¡No te lo pierdas!''',
                'resumen': 'Chef italiano Marco Antonelli prepara menú especial de 5 tiempos.',
                'tipo_noticia': 'chef',
                'imagen_destacada': 'https://images.unsplash.com/photo-1577219491135-ce391730fb2c?w=600&h=400&fit=crop',
                'destacada': True
            },
            {
                'titulo': '🏆 Reconocimiento a la Mejor Hamburguesa de la Ciudad',
                'contenido': '''¡Estamos orgullosos de anunciar que nuestra hamburguesa "El Clásico" ha sido reconocida como la mejor hamburguesa de Medellín por la revista Gastronómico!

Este reconocimiento es el resultado de meses de trabajo perfeccionando cada detalle: desde la mezcla perfecta de carnes, hasta el pan brioche casero y nuestras salsas secretas.

Queremos agradecer a todos nuestros clientes por su apoyo y confianza. Este premio es para ustedes.

Ven a probar la hamburguesa premiada y descubre por qué somos los mejores.''',
                'resumen': 'Hamburguesa "El Clásico" reconocida como la mejor de Medellín.',
                'tipo_noticia': 'premio',
                'imagen_destacada': 'https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=600&h=400&fit=crop'
            },
            {
                'titulo': '🎉 Celebramos Nuestro 5º Aniversario',
                'contenido': '''¡Cinco años compartiendo sabores únicos con ustedes! En este aniversario queremos agradecer a toda nuestra comunidad por hacer posible este sueño.

Durante esta semana especial tendremos:
- Descuentos especiales en todos nuestros platos
- Música en vivo todos los días
- Sorteos de cenas románticas
- Degustaciones gratuitas

Acompáñanos en esta celebración que es de todos nosotros.''',
                'resumen': 'Celebración del 5º aniversario con descuentos y eventos especiales.',
                'tipo_noticia': 'evento',
                'imagen_destacada': 'https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=600&h=400&fit=crop'
            }
        ]

        for i, noticia_data in enumerate(noticias_data):
            restaurante = restaurantes[i % len(restaurantes)]
            noticia_data['restaurante'] = restaurante
            if admin_user:
                noticia_data['autor'] = admin_user
            
            noticia, created = NoticiaRestaurante.objects.get_or_create(
                titulo=noticia_data['titulo'],
                defaults=noticia_data
            )
            if created:
                self.stdout.write(f"✓ Creada noticia: {noticia.titulo}")

        self.stdout.write(
            self.style.SUCCESS('¡Datos de ejemplo creados exitosamente!')
        )
        self.stdout.write("Ahora puedes:")
        self.stdout.write("- Visitar /promociones/ para ver las promociones")
        self.stdout.write("- Visitar /promociones/noticias/ para ver las noticias")
        self.stdout.write("- Visitar /promociones/todas/ para el dashboard combinado")
        self.stdout.write("- Acceder al admin para gestionar el contenido")