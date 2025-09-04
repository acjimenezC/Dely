from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


# User_Types
class UserType(models.Model):
    description = models.CharField(max_length=20)

    def __str__(self):
        return self.description




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
    
    def __str__(self):
        return self.business_name
    
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


