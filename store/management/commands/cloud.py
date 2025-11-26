import requests
from django.core.management.base import BaseCommand
from store.models import Product, Brand, Category, ImageGallery
from decimal import Decimal

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        response = requests.get('https://dummyjson.com/products')
        data = response.json()

        for p in data.get('products', []):  # safe fallback
            # Safe brand
            brand_name = p.get('brand', 'Unknown')
            brand_obj, _ = Brand.objects.get_or_create(
                title=brand_name,
                defaults={
                    "keyword": brand_name,
                    "description": brand_name,
                }
            )

            # Safe category
            category_name = p.get('category', 'General')
            category_obj, _ = Category.objects.get_or_create(
                title=category_name,
                defaults={
                    "keyword": category_name,
                    "description": category_name,
                }
            )

            # Safe price conversion
            price = Decimal(f"{p.get('price', 0):.2f}")
            old_price = Decimal(f"{(p.get('price', 0) + 100):.2f}")
            discount = int(p.get('discountPercentage', 0))

            # Create product
            product = Product.objects.create(
                title=p.get('title', 'No Title'),
                description=p.get('description', ''),
                old_price=old_price,
                sale_price=price,
                discount_percent=discount,
                available_stock=p.get('stock', 0),
                brand=brand_obj,
                category=category_obj,
                image=p.get('thumbnail', ''),  # URL
            )

            # Product images
            for img_url in p.get('images', []):
                ImageGallery.objects.create(
                    product=product,
                    image=img_url
                )
