from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


# Business_Types
class BusinessType(models.Model):
    description = models.CharField(max_length=20)

    def __str__(self):
        return self.description


# Businesses
class Business(models.Model):
    business_name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    description = models.TextField()
    phone_number = models.CharField(max_length=30)
    email = models.CharField(max_length=50)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    business_type = models.ForeignKey(BusinessType, on_delete=models.CASCADE)
    image_url = models.CharField(max_length=100, blank=True, null=True)
    
    # Ubicación geográfica (para filtrar por cercanía)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Latitud del negocio (ej: 6.2442)")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Longitud del negocio (ej: -75.5812)")
    
    def __str__(self):
        return self.business_name

    def calcular_distancia(self, user_lat, user_lon):
        """Calcula la distancia en km desde las coordenadas del usuario usando la fórmula de Haversine."""
        if not self.latitude or not self.longitude:
            return None
        
        from math import radians, sin, cos, sqrt, atan2
        
        # Convertir a radianes
        lat1, lon1 = radians(float(self.latitude)), radians(float(self.longitude))
        lat2, lon2 = radians(float(user_lat)), radians(float(user_lon))
        
        # Fórmula de Haversine
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        # Radio de la Tierra en km
        R = 6371
        distancia = R * c
        
        return round(distancia, 2)

    def average_rating(self):
        reviews = self.review_set.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 2)
        return None

    average_rating.short_description = 'Promedio de Calificación'
    
class BusinessImage(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='images')
    image_url = models.CharField(max_length=100)  # Guarda solo el nombre, ej: 'cafe_sol.jpg'

    def __str__(self):
        return f"Imagen de {self.business.business_name}: {self.image_url}"

    from django.core.validators import MinValueValidator, MaxValueValidator

    class Rating(models.Model):
        user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
        business = models.ForeignKey('Business', on_delete=models.CASCADE, related_name='ratings')
        stars = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        class Meta:
            unique_together = ('user', 'business')

        def __str__(self):
            return f"{self.user} - {self.business} ({self.stars} estrellas)"

# Favorites
class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'business')  

    def __str__(self):
        return f"{self.user}  {self.business}"


# Reviews
class Review(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  # 1–5
    comment = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    reply = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)   
    reports = models.IntegerField(default=0)    

    def __str__(self):
        return f"Review by {self.user} for {self.business}"


# Points
class Point(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.IntegerField()  
    description = models.CharField(max_length=50)
    registration_date = models.DateTimeField(auto_now_add=True)
    movement_type = models.CharField(max_length=10)  # 'earn' o 'redeem'


    def __str__(self):
     return f"{self.amount} points for {self.user}"


