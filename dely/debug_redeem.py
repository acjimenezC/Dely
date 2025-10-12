import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dely.settings')
import sys
django.setup()
from django.test import Client
from django.contrib.auth import get_user_model
from appdely.models import BusinessType, Business, Discount, Point, Redemption

User = get_user_model()

# Limpia posibles datos previos en DB (no, usar DB real)

# Crear usuario
user = User.objects.create_user(username='debugger', password='pass')
# Crear business type y business
bt = BusinessType.objects.create(description='Tipo')
b = Business.objects.create(business_name='DebugPlace', address='addr', description='d', phone_number='p', email='e', business_type=bt)
# Crear descuento
discount = Discount.objects.create(business=b, title='PromoDebug', description='desc', points_cost=50)
# Crear puntos
Point.objects.create(user=user, amount=100, description='initial debug', movement_type='earn')

client = Client()
login_ok = client.login(username='debugger', password='pass')
print('login_ok =', login_ok)
print('user total before =', user.total_points())
url = f"/discounts/redeem/{discount.id}/"
print('POST to', url)
resp = client.post(url)
print('status_code =', resp.status_code)
try:
    print('resp.url =', resp.url)
except Exception as e:
    print('no resp.url', e)
print('Redemption exists:', Redemption.objects.filter(user=user, discount=discount).exists())
print('Points list:', list(Point.objects.filter(user=user).values_list('amount', flat=True)))

print('Done')
