import csv
import os
import re
import unicodedata
from collections import defaultdict
from django.core.management.base import BaseCommand
from django.conf import settings
from appdely.models import Business, BusinessType, BusinessImage

class Command(BaseCommand):
    help = "Carga restaurantes completos desde CSVs directamente a la base de datos"

    def handle(self, *args, **kwargs):
        # --- Función para normalizar nombres ---
        def normalize_name(s):
            if not s:
                return ""
            s = s.lower().strip()
            s = unicodedata.normalize("NFKD", s)
            s = s.encode("ascii", "ignore").decode("ascii")  # quita tildes
            s = s.replace("&", "and").replace(".", " ")
            s = re.sub(r"[^\w\s]", " ", s)  # elimina puntuación
            s = re.sub(r"\s+", " ", s).strip()
            return s

        # Rutas de archivos
        images_file = os.path.join(settings.BASE_DIR, "imagenes_restaurantes.csv")
        descriptions_file = os.path.join(settings.BASE_DIR, "descripcion_restaurantes.csv")

        # --- 1. Cargar imágenes en memoria ---
        images_dict = defaultdict(list)
        if os.path.exists(images_file):
            try:
                with open(images_file, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        name = row.get("Business_Nombre", "")
                        url = row.get("Imagen_URL", "")
                        if url and url.strip():
                            norm_name = normalize_name(name)
                            images_dict[norm_name].append(url.strip())
                self.stdout.write(f"📷 Imágenes cargadas: {len(images_dict)} restaurantes")
            except Exception as e:
                self.stderr.write(f"Error leyendo imágenes: {e}")
                return
        else:
            self.stdout.write("⚠️ Archivo de imágenes no encontrado, continuando sin imágenes")

        # --- 2. Procesar restaurantes desde descripciones ---
        if not os.path.exists(descriptions_file):
            self.stderr.write(self.style.ERROR(f"Archivo requerido no encontrado: {descriptions_file}"))
            return

        try:
            with open(descriptions_file, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                
                created_count = 0
                updated_count = 0
                
                for row in reader:
                    business_name = row.get("business_name", "").strip()
                    if not business_name:
                        continue
                    
                    address = row.get("address", "")
                    description = row.get("description", "")
                    phone = row.get("phone_number", "")
                    email = row.get("email", "")
                    status = row.get("status", "True") in ["True", "1", "true"]
                    type_desc = row.get("business_type", "Restaurante")

                    # Crear o obtener tipo de negocio
                    business_type, _ = BusinessType.objects.get_or_create(description=type_desc)

                    # Crear o actualizar negocio
                    business, created = Business.objects.update_or_create(
                        business_name=business_name,
                        defaults={
                            "address": address,
                            "description": description,
                            "phone_number": phone,
                            "email": email,
                            "status": status,
                            "business_type": business_type,
                        }
                    )

                    if created:
                        created_count += 1
                        self.stdout.write(f"✅ Creado: {business_name}")
                    else:
                        updated_count += 1
                        self.stdout.write(f"🔄 Actualizado: {business_name}")

                    # --- 3. Agregar imágenes al negocio ---
                    norm_name = normalize_name(business_name)
                    urls = images_dict.get(norm_name, [])
                    
                    for url in urls:
                        # Evitar duplicados
                        if not BusinessImage.objects.filter(business=business, image_url=url).exists():
                            BusinessImage.objects.create(
                                business=business,
                                image_url=url
                            )
                    
                    if urls:
                        self.stdout.write(f"   📷 {len(urls)} imágenes agregadas")

                # Resumen final
                self.stdout.write(self.style.SUCCESS(f"\n🎉 Proceso completado:"))
                self.stdout.write(f"   • Restaurantes creados: {created_count}")
                self.stdout.write(f"   • Restaurantes actualizados: {updated_count}")
                self.stdout.write(f"   • Total procesados: {created_count + updated_count}")

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error procesando restaurantes: {e}"))