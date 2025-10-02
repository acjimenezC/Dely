from django.contrib import admin
from .models import TipoPromocion, Promocion, NoticiaRestaurante, UsuarioPromocion


@admin.register(TipoPromocion)
class TipoPromocionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)


@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'restaurante', 'tipo_promocion', 'fecha_inicio', 'fecha_fin', 'activa', 'vistas', 'usos_actuales')
    list_filter = ('activa', 'tipo_promocion', 'fecha_inicio', 'fecha_fin', 'restaurante__business_type')
    search_fields = ('titulo', 'descripcion', 'restaurante__business_name')
    date_hierarchy = 'fecha_inicio'
    readonly_fields = ('vistas', 'usos_actuales', 'creada_en', 'actualizada_en')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'descripcion', 'descripcion_corta', 'restaurante', 'tipo_promocion')
        }),
        ('Detalles de Promoción', {
            'fields': ('descuento_porcentaje', 'precio_original', 'precio_promocional')
        }),
        ('Fechas y Horarios', {
            'fields': ('fecha_inicio', 'fecha_fin', 'hora_inicio', 'hora_fin', 'dias_validos')
        }),
        ('Limitaciones', {
            'fields': ('activa', 'limite_personas', 'usos_actuales')
        }),
        ('Multimedia', {
            'fields': ('imagen_principal', 'imagen_secundaria')
        }),
        ('Términos', {
            'fields': ('terminos_condiciones',)
        }),
        ('Metadata', {
            'fields': ('creada_por', 'vistas', 'me_gusta', 'creada_en', 'actualizada_en'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo objeto
            obj.creada_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(NoticiaRestaurante)
class NoticiaRestauranteAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo_noticia', 'restaurante', 'fecha_publicacion', 'activa', 'destacada', 'vistas')
    list_filter = ('activa', 'destacada', 'tipo_noticia', 'fecha_publicacion', 'restaurante__business_type')
    search_fields = ('titulo', 'contenido', 'restaurante__business_name')
    date_hierarchy = 'fecha_publicacion'
    readonly_fields = ('vistas', 'me_gusta', 'compartidas', 'creada_en', 'actualizada_en')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'subtitulo', 'resumen', 'tipo_noticia', 'restaurante')
        }),
        ('Contenido', {
            'fields': ('contenido',)
        }),
        ('Multimedia', {
            'fields': ('imagen_destacada', 'galeria_imagenes')
        }),
        ('Publicación', {
            'fields': ('fecha_publicacion', 'activa', 'destacada', 'autor')
        }),
        ('Engagement', {
            'fields': ('vistas', 'me_gusta', 'compartidas'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('creada_en', 'actualizada_en'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo objeto
            obj.autor = request.user
        super().save_model(request, obj, form, change)


@admin.register(UsuarioPromocion)
class UsuarioPromocionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'promocion', 'fecha_uso', 'calificacion')
    list_filter = ('fecha_uso', 'calificacion', 'promocion__tipo_promocion')
    search_fields = ('usuario__username', 'promocion__titulo')
    date_hierarchy = 'fecha_uso'
    readonly_fields = ('fecha_uso',)
