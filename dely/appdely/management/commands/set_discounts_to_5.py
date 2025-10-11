from django.core.management.base import BaseCommand
from appdely.models import Discount

class Command(BaseCommand):
    help = 'Set all existing discounts points_cost to 5'

    def handle(self, *args, **options):
        updated = Discount.objects.update(points_cost=5)
        self.stdout.write(self.style.SUCCESS(f'Updated {updated} discounts to 5 points.'))
