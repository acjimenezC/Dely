import os
import csv
from openai import OpenAI
from django.core.management.base import BaseCommand
from django.conf import settings
from dotenv import load_dotenv
from appdely.models import Business, BusinessType  # ✅ Corregido: tu app se llama 'appdely'

class Command(BaseCommand):
    help = "Update or create restaurant/cafe descriptions from CSV using OpenAI API"

    def handle(self, *args, **kwargs):
        # ✅ Load environment variables from the .env file
        load_dotenv()  # Carga desde .env en el directorio actual (dely/)

        # ✅ Initialize the OpenAI client
        api_key = os.environ.get("OPENAI_API_KEY")  # Variable estándar de OpenAI
        
        if not api_key:
            self.stderr.write(self.style.ERROR("❌ OPENAI_API_KEY no encontrada en las variables de entorno"))
            self.stderr.write("Crea un archivo .env con: OPENAI_API_KEY=tu_api_key_aquí")
            return

        client = OpenAI(api_key=api_key)

        # ✅ Helper function to send prompt and get completion from OpenAI
        def get_completion(prompt, model="gpt-3.5-turbo"):
            messages = [{"role": "user", "content": prompt}]
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )
            return response.choices[0].message.content.strip()

        # ✅ Instruction to guide the AI
        instruction = (
            "Eres un experto en marketing gastronómico. "
            "Vas a reescribir descripciones de restaurantes o cafés en menos de 100 palabras, "
            "de manera atractiva, clara y profesional para usarse en una aplicación. "
            "Incluye tipo de cocina, ambiente o concepto si aplica."
        )

        # ✅ Ruta al archivo CSV
        csv_path = os.path.join(settings.BASE_DIR, "descripcion_restaurantes.csv")

        if not os.path.exists(csv_path):
            self.stderr.write(self.style.ERROR(f"CSV not found: {csv_path}"))
            return

        # ✅ Leer CSV
        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                name = row.get("business_name")
                address = row.get("address")
                description = row.get("description", "")
                phone = row.get("phone_number")
                email = row.get("email")
                status = row.get("status", "True") in ["True", "1", "true"]
                type_desc = row.get("business_type")

                self.stdout.write(f"Procesando: {name}")

                try:
                    # ✅ Buscar o crear tipo de negocio
                    business_type, _ = BusinessType.objects.get_or_create(description=type_desc)

                    # ✅ Prompt para la IA (temporalmente desactivado)
                    # prompt = (
                    #     f"{instruction} "
                    #     f"Descripción original: '{description}'. "
                    #     f"Nombre del negocio: '{name}'."
                    # )

                    # ✅ Obtener descripción mejorada (temporalmente usar descripción original)
                    # updated_description = get_completion(prompt)
                    updated_description = description or f"Restaurante {name} - Excelente lugar para disfrutar de buena comida en un ambiente acogedor."

                    # ✅ Guardar en DB
                    business, created = Business.objects.update_or_create(
                        business_name=name,
                        defaults={
                            "address": address,
                            "description": updated_description,
                            "phone_number": phone,
                            "email": email,
                            "status": status,
                            "business_type": business_type,
                        },
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Creado: {business.business_name}"))
                    else:
                        self.stdout.write(self.style.SUCCESS(f"Actualizado: {business.business_name}"))

                except Exception as e:
                    self.stderr.write(f"❌ Error con {name}: {str(e)}")