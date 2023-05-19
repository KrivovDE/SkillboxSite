from django.core.management import BaseCommand

from shopapp.models import Order, Product


class Command(BaseCommand):
    """
    Update order
    """

    def handle(self, *args, **options):
        self.stdout.write("Update orders")

        order = Order.objects.first()
        products = Product.objects.all()

        for product in products:
            order.products.add(product)
        order.save()

        self.stdout.write(self.style.SUCCESS(f"Orders created {order.products.all()}"))
