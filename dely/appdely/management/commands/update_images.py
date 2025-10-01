import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from collections import defaultdict
from appdely.models import Business, BusinessImage

class Command(BaseCommand):
    help = "Lee imagenes_restaurantes.csv y asigna múltiples URLs a cada Business"

    def handle(self, *args, **kwargs):
        # ✅ Ruta absoluta al archivo CSV
        csv_file = os.path.join(settings.BASE_DIR, "imagenes_restaurantes.csv")
        
        if not os.path.exists(csv_file):
            self.stderr.write(self.style.ERROR(f"Archivo no encontrado: {csv_file}"))
            return

        # Agrupamos URLs por restaurante
        images_by_business = defaultdict(list)

        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                business = row.get("Business_Nombre")
                url = row.get("Imagen_URL")

                if business and url:
                    images_by_business[business].append(url.strip())

        # Recorremos negocios encontrados en el CSV
        for business_name, urls in images_by_business.items():
            try:
                business = Business.objects.get(business_name=business_name)

                for url in urls:
                    # Evitar duplicados
                    if not BusinessImage.objects.filter(business=business, image_url=url).exists():
                        BusinessImage.objects.create(
                            business=business,
                            image_url=url
                        )

                self.stdout.write(self.style.SUCCESS(
                    f"{business.business_name}: {len(urls)} imágenes procesadas"
                ))

            except Business.DoesNotExist:
                self.stderr.write(f"No existe en BD: {business_name}")

        self.stdout.write(self.style.SUCCESS("✅ Proceso terminado"))
