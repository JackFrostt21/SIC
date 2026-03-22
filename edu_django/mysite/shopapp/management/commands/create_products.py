from django.core.management.base import BaseCommand

from shopapp.models import Product


class Command(BaseCommand):
    """
    Creates products
    """
    def handle(self, *args, **options):
        self.stdout.write('Create products')

        products_names = [
            'Laptop',
            'Desktop',
            'SmartPhone',
        ]

        for products_name in products_names:
            product, created = Product.objects.get_or_create(name=products_name)
            self.stdout.write(f'Created product {product.name}')

        self.stdout.write(self.style.SUCCESS('Products created'))