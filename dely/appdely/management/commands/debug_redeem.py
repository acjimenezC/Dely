from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from appdely.models import BusinessType, Business, Discount, Point, Redemption
from django.test import Client

class Command(BaseCommand):
    help = 'Debug redemption flow (creates data and attempts redeem)'

    def handle(self, *args, **options):
        User = get_user_model()
        import time
        uname = f'debugger_{int(time.time())}'
        user, created = User.objects.get_or_create(username=uname)
        if created:
            user.set_password('pass')
            user.save()
        bt = BusinessType.objects.create(description='Tipo')
        b = Business.objects.create(business_name='DebugPlace', address='addr', description='d', phone_number='p', email='e', business_type=bt)
        discount = Discount.objects.create(business=b, title='PromoDebug', description='desc', points_cost=50)
        Point.objects.create(user=user, amount=100, description='initial debug', movement_type='earn')

        client = Client()
        login_ok = client.login(username='debugger', password='pass')
        self.stdout.write(f'login_ok={login_ok}')
        self.stdout.write(f'user total before={user.total_points()}')
        url = f'/discounts/redeem/{discount.id}/'
        resp = client.post(url, {}, HTTP_HOST='127.0.0.1')
        self.stdout.write(f'status_code={resp.status_code}')
        try:
            self.stdout.write(f'response.content={resp.content.decode("utf-8")[:500]}')
        except Exception:
            pass
        # fetch fresh user from DB
        user2 = User.objects.get(username=uname)
        self.stdout.write(f'Redemption exists (fresh): {Redemption.objects.filter(user=user2, discount=discount).exists()}')
        self.stdout.write(f'Points list (fresh): {list(Point.objects.filter(user=user2).values_list("amount", flat=True))}')
