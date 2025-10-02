from django.db import models
from django.utils import timezone
from django.conf import settings
from appdely.models import Business


class TipoPromocion(models.Model):
    """Tipos de promociones: Descuento, 2x1, Combo, Evento especial, etc."""
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Tipo de Promoción"
        verbose_name_plural = "Tipos de Promociones"


class Promocion(models.Model):
    """Promociones de restaurantes y locales de comida"""
    
    # Información básica
    titulo = models.CharField(max_length=200, help_text="Título llamativo de la promoción")
    descripcion = models.TextField(help_text="Descripción detallada de la promoción")
    descripcion_corta = models.CharField(max_length=150, help_text="Descripción breve para tarjetas")
    
    # Relaciones
    restaurante = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='promociones')
    tipo_promocion = models.ForeignKey(TipoPromocion, on_delete=models.CASCADE)
    
    # Detalles de la promoción
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Ej: 25.00 para 25%")
    precio_original = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    precio_promocional = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Fechas y tiempo
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    hora_inicio = models.TimeField(blank=True, null=True, help_text="Hora de inicio diaria")
    hora_fin = models.TimeField(blank=True, null=True, help_text="Hora de fin diaria")
    
    # Días de la semana (para promociones recurrentes)
    dias_validos = models.CharField(max_length=20, default="1234567", help_text="1=Lunes, 7=Domingo")
    
    # Estado y limitaciones
    activa = models.BooleanField(default=True)
    limite_personas = models.PositiveIntegerField(blank=True, null=True, help_text="Límite de personas que pueden usar la promoción")
    usos_actuales = models.PositiveIntegerField(default=0)
    
    # Contenido multimedia
    imagen_principal = models.URLField(blank=True, null=True)
    imagen_secundaria = models.URLField(blank=True, null=True)
    
    # Términos y condiciones
    terminos_condiciones = models.TextField(blank=True, help_text="Términos y condiciones específicos")
    
    # Metadata
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)
    creada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Engagement
    vistas = models.PositiveIntegerField(default=0)
    me_gusta = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.titulo} - {self.restaurante.business_name}"
    
    def esta_activa(self):
        """Verifica si la promoción está activa considerando fechas, horas y límites"""
        hoy = timezone.now().date()
        ahora = timezone.now().time()
        
        # Verificar fechas
        if not (self.fecha_inicio <= hoy <= self.fecha_fin):
            return False
        
        # Verificar si está marcada como activa
        if not self.activa:
            return False
        
        # Verificar límite de usos
        if self.limite_personas and self.usos_actuales >= self.limite_personas:
            return False
        
        # Verificar día de la semana (1=Lunes, 7=Domingo)
        dia_semana = str(hoy.isoweekday())
        if dia_semana not in self.dias_validos:
            return False
        
        # Verificar horario si está definido
        if self.hora_inicio and self.hora_fin:
            if not (self.hora_inicio <= ahora <= self.hora_fin):
                return False
        
        return True
    
    def calcular_descuento(self):
        """Calcula el porcentaje de descuento si hay precios"""
        if self.precio_original and self.precio_promocional:
            descuento = ((self.precio_original - self.precio_promocional) / self.precio_original) * 100
            return round(descuento, 2)
        return self.descuento_porcentaje
    
    def tiempo_restante(self):
        """Devuelve los días restantes de la promoción"""
        hoy = timezone.now().date()
        if self.fecha_fin > hoy:
            return (self.fecha_fin - hoy).days
        return 0
    
    def incrementar_vistas(self):
        """Incrementa el contador de vistas"""
        self.vistas += 1
        self.save(update_fields=['vistas'])
    
    def incrementar_uso(self):
        """Incrementa el contador de usos"""
        self.usos_actuales += 1
        self.save(update_fields=['usos_actuales'])
    
    class Meta:
        verbose_name = "Promoción"
        verbose_name_plural = "Promociones"
        ordering = ['-creada_en']


class NoticiaRestaurante(models.Model):
    """Noticias relacionadas con restaurantes, nuevos platos, eventos, etc."""
    
    TIPO_NOTICIA_CHOICES = [
        ('nuevo_plato', 'Nuevo Plato'),
        ('evento', 'Evento Especial'),
        ('apertura', 'Nueva Apertura'),
        ('renovacion', 'Renovación'),
        ('chef', 'Chef Invitado'),
        ('premio', 'Premio/Reconocimiento'),
        ('general', 'Noticia General'),
    ]
    
    # Información básica
    titulo = models.CharField(max_length=200)
    subtitulo = models.CharField(max_length=300, blank=True)
    contenido = models.TextField()
    resumen = models.CharField(max_length=200, help_text="Resumen para vista previa")
    
    # Relaciones
    restaurante = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='noticias', blank=True, null=True)
    tipo_noticia = models.CharField(max_length=20, choices=TIPO_NOTICIA_CHOICES, default='general')
    
    # Multimedia
    imagen_destacada = models.URLField(blank=True, null=True)
    galeria_imagenes = models.TextField(blank=True, help_text="URLs de imágenes separadas por comas")
    
    # Publicación
    fecha_publicacion = models.DateTimeField(default=timezone.now)
    activa = models.BooleanField(default=True)
    destacada = models.BooleanField(default=False, help_text="Mostrar en banner principal")
    
    # Metadata
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)
    
    # Engagement
    vistas = models.PositiveIntegerField(default=0)
    me_gusta = models.PositiveIntegerField(default=0)
    compartidas = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.titulo
    
    def incrementar_vistas(self):
        """Incrementa el contador de vistas"""
        self.vistas += 1
        self.save(update_fields=['vistas'])
    
    def obtener_galeria(self):
        """Devuelve lista de URLs de la galería"""
        if self.galeria_imagenes:
            return [url.strip() for url in self.galeria_imagenes.split(',') if url.strip()]
        return []
    
    class Meta:
        verbose_name = "Noticia de Restaurante"
        verbose_name_plural = "Noticias de Restaurantes"
        ordering = ['-fecha_publicacion']


class UsuarioPromocion(models.Model):
    """Registro de usuarios que han usado promociones"""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    promocion = models.ForeignKey(Promocion, on_delete=models.CASCADE)
    fecha_uso = models.DateTimeField(auto_now_add=True)
    calificacion = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], blank=True, null=True)
    comentario = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.promocion.titulo}"
    
    class Meta:
        verbose_name = "Uso de Promoción"
        verbose_name_plural = "Usos de Promociones"
        unique_together = ('usuario', 'promocion')
     
