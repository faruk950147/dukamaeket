# store/context_processors.py
from .models import Category, Product, Brand
from django.db.models import Max, Min

def store_context(request):
    categories = Category.objects.filter(parent=None, status='active').prefetch_related(
        'children',
        'children__children'
    )
    cat_ids = Product.objects.values_list('category__id', flat=True).distinct()
    cats = Category.objects.filter(id__in=cat_ids, status='active')
    cates = cats.filter(is_featured=True)[:3]

    brand_ids = Product.objects.values_list('brand__id', flat=True).distinct()
    brands = Brand.objects.filter(id__in=brand_ids, status='active', is_featured=True)

    max_price = Product.objects.aggregate(Max('sale_price'))['sale_price__max']
    min_price = Product.objects.aggregate(Min('sale_price'))['sale_price__min']

    return {
        'categories': categories,
        'cats': cats,
        'cates': cates,
        'brands': brands,
        'max_price': max_price,
        'min_price': min_price
    }
