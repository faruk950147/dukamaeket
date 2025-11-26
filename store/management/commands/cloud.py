import requests
from django.core.management.base import BaseCommand
from store.models import Product, Brand, Category, ImageGallery
from decimal import Decimal

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        response = requests.get('https://dummyjson.com/products')
        data = response.json()

        for p in data['products']:

            # Brand create/get
            brand_obj, _ = Brand.objects.get_or_create(
                title=p['brand'],
                defaults={
                    "keyword": p['brand'],
                    "description": p['brand'],
                }
            )

            # Category create/get
            category_obj, _ = Category.objects.get_or_create(
                title=p['category'],
                defaults={
                    "keyword": p['category'],
                    "description": p['category'],
                }
            )

            # Product create
            product = Product.objects.create(
                title=p['title'],
                description=p['description'],
                old_price=Decimal(p['price']) + 100,     # Just example
                sale_price=Decimal(p['price']),
                discount_percent=int(p['discountPercentage']),
                available_stock=p['stock'],
                brand=brand_obj,
                category=category_obj,
                image=p['thumbnail'],  # URL image assign
            )

            # Product Gallery Images save
            for img_url in p['images']:
                ImageGallery.objects.create(
                    product=product,
                    image=img_url
                )
