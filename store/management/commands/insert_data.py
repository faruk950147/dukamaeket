import keyword
from django.core.management.base import BaseCommand
from faker import Faker
from decimal import Decimal
from django.utils import timezone
import random

from store.models import Category, Brand, Product

fake = Faker()


# ---------------------------------------------------------
# SEED CATEGORIES (STATIC)
# ---------------------------------------------------------
def seed_categories():
    Category.objects.all().delete()

    data = [
        {"id": 1, "title": "Clothing Accessories", "parent": None},
        {"id": 2, "title": "Women Clothing Accessories", "parent": 1},
        {"id": 3, "title": "Lehenga Collections", "parent": 2},
        {"id": 4, "title": "Sallowar Kameez Collections", "parent": 2},
        {"id": 5, "title": "Burkha Collections", "parent": 2},

        {"id": 6, "title": "Men Clothing Accessories", "parent": 1},
        {"id": 7, "title": "Shirt Collections", "parent": 6},
        {"id": 8, "title": "T-Shirt", "parent": 6},

        {"id": 9, "title": "Jewelers Accessories", "parent": None},
        {"id": 10, "title": "Necklace", "parent": 9},
        {"id": 11, "title": "Ear Rings", "parent": 9},

        {"id": 12, "title": "Bridal", "parent": 10},
        {"id": 13, "title": "Classic", "parent": 10},
        {"id": 14, "title": "Bridal Rings", "parent": 11},
        {"id": 15, "title": "Classic Rings", "parent": 11},

        {"id": 16, "title": "Electronics", "parent": None},
        {"id": 17, "title": "Laptops", "parent": 16},
    ]

    created = {}

    # create all categories
    for item in data:
        cat = Category(
            title=item["title"],
            keyword="N/A",
            description="N/A",
            parent=None,
            status="active",
            is_featured=False,
            image="defaults/default.jpg",
        )
        cat.save()
        created[item["id"]] = cat

    # update parents
    for item in data:
        if item["parent"]:
            child = created[item["id"]]
            parent = created[item["parent"]]
            child.parent = parent
            child.save()

    print("Categories seeded successfully!")


# ---------------------------------------------------------
# SEED BRANDS (STATIC)
# ---------------------------------------------------------
def seed_brands():
    Brand.objects.all().delete()

    brands = ["Duba", "KngPn", "Gap", "Asus", "Hp"]

    for name in brands:
        Brand.objects.create(
            title=name,
            keyword="N/A",
            description="N/A",
            image="defaults/default.jpg",
            status="active",
            is_featured=False
        )

    print("Brands seeded successfully!")


# ---------------------------------------------------------
# SEED PRODUCTS (STATIC)
# ---------------------------------------------------------
def seed_products():
    Product.objects.all().delete()

    products = [
        {
            "title": "Exclusive Design Readymade Georgette Embroidered Party Dress02",
            "slug": "exclusive-design-readymade-georgette-embroidered-party-dress02",
            "category": "Lehenga Collections",
            "brand": "Duba",
            "old_price": "50000000.00",
            "sale_price": "40000000.00",
            "discount_percent": 20,
            "available_stock": 10,
        },
        {
            "title": "Exclusive Desighn Indian Handmade new designer embroidery",
            "slug": "exclusive-desighn-indian-handmade-new-designer-embroidery",
            "category": "Lehenga Collections",
            "brand": "Duba",
            "old_price": "50000000.00",
            "sale_price": "40000000.00",
            "discount_percent": 20,
            "available_stock": 10,
        },
        {
            "title": "Latest Designer Ready to Wear Lehenga Choli with Heavy Embroidery",
            "slug": "latest-designer-ready-to-wear-lehenga-choli-with-heavy-embroidery",
            "category": "Lehenga Collections",
            "brand": "KngPn",
            "old_price": "50000.00",
            "sale_price": "40000.00",
            "discount_percent": 20,
            "available_stock": 10,
        },
        {
            "title": "Latest & Exclusive Luxury Stylish Glorious Design Silk saree with",
            "slug": "latest-exclusive-luxury-stylish-glorious-design-silk-saree-with",
            "category": "Lehenga Collections",
            "brand": "Gap",
            "old_price": "1000.00",
            "sale_price": "500.00",
            "discount_percent": 50,
            "available_stock": 3,
        },

        # ------- Sallowar Kameez ---------
        {
            "title": "Most Demanding 2-Pices Dress AC cotton TWO Piece Stitched",
            "slug": "most-demanding-2-pices-dress-ac-cotton-two-piece-stitched",
            "category": "Sallowar Kameez Collections",
            "brand": "Duba",
            "old_price": "50000000.00",
            "sale_price": "40000000.00",
            "discount_percent": 20,
            "available_stock": 10,
        },

        # ------- Burkha Collections -------
        {
            "title": "New Stylish High-Quality Pokio Hijab & Borka",
            "slug": "new-stylish-high-quality-pokio-hijab-borka",
            "category": "Burkha Collections",
            "brand": "Duba",
            "old_price": "1000.00",
            "sale_price": "500.00",
            "discount_percent": 50,
            "available_stock": 6,
        },

        # ------- Electronics -------
        {
            "title": "Asus X47Z",
            "slug": "asus-x47z",
            "category": "Electronics",
            "brand": "Asus",
            "old_price": "1000.00",
            "sale_price": "930.00",
            "discount_percent": 7,
            "available_stock": 0,
        },

        # ------- Laptops -------
        {
            "title": "Hp T 55V",
            "slug": "hp-t-55v",
            "category": "Laptops",
            "brand": "Hp",
            "old_price": "1000.00",
            "sale_price": "950.00",
            "discount_percent": 5,
            "available_stock": 0,
        },
    ]

    for item in products:
        category = Category.objects.get(title=item["category"])
        brand = Brand.objects.get(title=item["brand"])

        Product.objects.create(
            title=item["title"],
            slug=item["slug"],
            category=category,
            brand=brand,
            old_price=Decimal(item["old_price"]),
            sale_price=Decimal(item["sale_price"]),
            discount_percent=item["discount_percent"],
            available_stock=item["available_stock"],
            prev_des="N/A",
            add_des="N/A",
            short_des="N/A",
            long_des="N/A",
            keyword="N/A",
            description="N/A",
            
            deadline=None,
            is_deadline=False,
            is_featured=False,
            status="active",
        )

    print("Products seeded successfully!")


# ---------------------------------------------------------
# MANAGEMENT COMMAND
# ---------------------------------------------------------
class Command(BaseCommand):
    help = "Seed Categories, Brands, and Products"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding Categories...")
        seed_categories()

        self.stdout.write("Seeding Brands...")
        seed_brands()

        self.stdout.write("Seeding Products...")
        seed_products()

        self.stdout.write(self.style.SUCCESS("Database seeding complete!"))
