from django.core.management.base import BaseCommand
from appdely.models import Business, Discount
import random

class Command(BaseCommand):
    help = 'Crear descuentos de ejemplo para hasta 5 negocios'

    def handle(self, *args, **options):
        businesses = Business.objects.all()[:5]
        if not businesses:
            self.stdout.write(self.style.WARNING('No hay negocios para crear descuentos.'))
            return

        for b in businesses:
            # Crear entre 1 y 3 descuentos por negocio
            for i in range(1, random.randint(1, 3) + 1):
                title = f"Descuento {i} en {b.business_name}"
                points_cost = 5
                Discount.objects.create(
                    business=b,
                    title=title,
                    description=f"Ahorra con {title}",
                    points_cost=points_cost,
                    active=True
                )
                self.stdout.write(self.style.SUCCESS(f'Creado {title} ({points_cost} pts)'))

        self.stdout.write(self.style.SUCCESS('Descuentos de ejemplo creados.'))
