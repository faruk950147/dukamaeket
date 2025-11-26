from django.core.management.base import BaseCommand
from faker import Faker
from decimal import Decimal
from django.utils import timezone
import random
from store.models import Category, Brand, Product

fake = Faker()

# -------------------------------
# CONFIG
# -------------------------------
NUM_CATEGORIES = 5
NUM_BRANDS = 5
NUM_PRODUCTS = 50

# -------------------------------
# SEED CATEGORIES
# -------------------------------
def seed_categories(n=NUM_CATEGORIES):
    Category.objects.all().delete()  

    for _ in range(n):
        cat = Category(
            title=fake.unique.word().capitalize(),
            keyword='N/A',
            description=fake.sentence(),
            image='defaults/default.jpg',
            status='active'
        )
        cat.save()  

# -------------------------------
# SEED BRANDS
# -------------------------------
def seed_brands(n=NUM_BRANDS):
    Brand.objects.all().delete()

    for _ in range(n):
        brand = Brand(
            title=fake.unique.company(),
            keyword='N/A',
            description=fake.sentence(),
            image='defaults/default.jpg',
            status='active'
        )
        brand.save()  

# -------------------------------
# SEED PRODUCTS
# -------------------------------
def seed_products(n=NUM_PRODUCTS):
    Product.objects.all().delete()

    categories = list(Category.objects.all())
    brands = list(Brand.objects.all())

    for _ in range(n):
        old_price = Decimal(random.randint(1000, 10000))
        discount_percent = random.randint(0, 50)
        sale_price = old_price - (old_price * Decimal(discount_percent) / Decimal(100))

        # Optional: 30% probability deadline
        if random.random() < 0.3:
            deadline = timezone.now() + timezone.timedelta(days=random.randint(1, 30))
            is_deadline = True
        else:
            deadline = None
            is_deadline = False

        product = Product(
            title=fake.unique.word().capitalize(),
            category=random.choice(categories),
            brand=random.choice(brands),
            old_price=old_price,
            sale_price=sale_price,
            discount_percent=discount_percent,
            available_stock=random.randint(1, 100),
            keyword='N/A',
            description=fake.text(max_nb_chars=200),
            image='defaults/default.jpg',
            deadline=deadline,
            is_deadline=is_deadline,
            is_featured=random.choice([True, False]),
            status='active'
        )
        product.save()  
# -------------------------------
# COMMAND
# -------------------------------
class Command(BaseCommand):
    help = 'Seed Categories, Brands, and Products into the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding Categories...')
        seed_categories()
        self.stdout.write('Seeding Brands...')
        seed_brands()
        self.stdout.write('Seeding Products...')
        seed_products()
        self.stdout.write(self.style.SUCCESS('Database seeding complete!'))
