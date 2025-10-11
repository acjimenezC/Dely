from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Business, Discount, Point, Redemption

User = get_user_model()


class RedemptionTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Crear usuario
        self.user = User.objects.create_user(username='tester', password='pass')
        # Crear negocio
        # crear un BusinessType requerido
        from .models import BusinessType
        bt = BusinessType.objects.create(description='Tipo')
        self.business = Business.objects.create(
            business_name='TestPlace', address='Somewhere', description='Desc', phone_number='123', email='a@b.c', business_type=bt
        )
        # Crear descuento (5 puntos)
        self.discount = Discount.objects.create(business=self.business, title='Promo', description='Desc', points_cost=5)
        # Dar puntos al usuario
        Point.objects.create(user=self.user, amount=100, description='initial', movement_type='earn')

    def test_redeem_discount(self):
        # Login
        self.client.login(username='tester', password='pass')
        url = reverse('appdely:redeem_discount', args=[self.discount.id])
        response = self.client.post(url)
        # Ahora devolvemos la página de éxito con QR
        self.assertEqual(response.status_code, 200)
        # Comprueba que exista el canje
        self.assertTrue(Redemption.objects.filter(user=self.user, discount=self.discount).exists())
        # Comprueba que se creó un Point negativo
        neg = Point.objects.filter(user=self.user, amount__lt=0).first()
        self.assertIsNotNone(neg)
        self.assertEqual(-neg.amount, self.discount.points_cost)
        # Verificar que el HTML contenga la referencia al QR (data URI o ruta estática)
        content = response.content.decode('utf-8')
        self.assertTrue('appdely/img/qr_redeem.png' in content or 'data:image/png;base64' in content)

    def test_redeem_insufficient_points(self):
        # Usuario con 0 puntos intenta canjear
        user2 = User.objects.create_user(username='poor', password='pass')
        # Login
        self.client.login(username='poor', password='pass')
        url = reverse('appdely:redeem_discount', args=[self.discount.id])
        response = self.client.post(url, follow=True)
        # Debe mostrar mensaje de error y no crear Redemption ni Point negativo
        self.assertFalse(Redemption.objects.filter(user=user2, discount=self.discount).exists())
        self.assertFalse(Point.objects.filter(user=user2, amount__lt=0).exists())
        # Buscar mensaje en la respuesta
        messages = list(response.context['messages'])
        self.assertTrue(any('No tienes puntos suficientes' in str(m) for m in messages))

    def test_my_redemptions_view(self):
        # Acceso sin login debe redirigir
        url = reverse('appdely:my_redemptions')
        response = self.client.get(url)
        self.assertIn(response.status_code, (302, 302))
        # Con login, debe responder 200
        self.client.login(username='tester', password='pass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Debe contener al menos la sección de 'Mis canjes' o el contexto
        self.assertIn('redemptions', response.context)
