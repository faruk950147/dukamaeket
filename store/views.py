from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Avg
from django.core.paginator import Paginator
from django.http import JsonResponse
from store.models import (
    Category,
    Brand,
    Product,
    Slider,
    AcceptancePayment,
    ProductVariant
)
import logging

logger = logging.getLogger('project')

# =========================================================
# HOME PAGE
# =========================================================
@method_decorator(never_cache, name='dispatch')
class HomeView(generic.View):
    def get(self, request):
        # Active sliders all fetch
        active_sliders = Slider.objects.filter(status='active')
        sliders = active_sliders[:4]
        feature_sliders = active_sliders.filter(slider_type='feature')[:4]
        add_sliders = active_sliders.filter(slider_type='add')[:2]
        promo_sliders = active_sliders.filter(slider_type='promotion')[:3]

        acceptance_payments = AcceptancePayment.objects.filter(status='active')[:4]
        brands = Brand.objects.filter(status='active', is_featured=True)
        cates = Category.objects.filter(status='active', children__isnull=True, is_featured=True)[:3]

        top_deals = list(Product.objects.filter(
            status='active', discount_percent__gt=0, is_deadline=True, deadline__gte=timezone.now()
        ).select_related('category', 'brand').prefetch_related('reviews') \
         .annotate(avg_rate=Avg('reviews__rating')).order_by('-discount_percent', 'deadline')[:6]
        )
        first_top_deal = top_deals[0] if top_deals else None

        featured_products = Product.objects.filter(
            status='active', is_featured=True
        ).select_related('category', 'brand').prefetch_related('reviews') \
         .annotate(avg_rate=Avg('reviews__rating'))[:5]


        context = {
            'sliders': sliders,
            'feature_sliders': feature_sliders,
            'add_sliders': add_sliders,
            'promo_sliders': promo_sliders,
            'acceptance_payments': acceptance_payments,
            'brands': brands,
            'cates': cates,
            'top_deals': top_deals,
            'first_top_deal': first_top_deal,
            'featured_products': featured_products,
        }
        return render(request, 'store/home.html', context)

# =========================================================
# PRODUCT DETAIL VIEW
# =========================================================
@method_decorator(never_cache, name='dispatch')
class ProductDetailView(generic.View):
    def get(self, request, id):
        product = get_object_or_404(
            Product.objects.select_related('category', 'brand')
                   .prefetch_related('reviews', 'variants__color', 'variants__size', 'images')
                   .annotate(avg_rate=Avg('reviews__rating')),
            id=id,
            status='active'
        )

        related_products = Product.objects.filter(
            category=product.category,
            status='active'
        ).exclude(id=product.id).select_related('category', 'brand') \
         .prefetch_related('reviews').annotate(avg_rate=Avg('reviews__rating'))[:4]

        context = {
            'product': product,
            'related_products': related_products
        }
        return render(request, 'store/product-detail.html', context)

# =========================================================
# SHOP VIEW WITH PAGINATION
# =========================================================
@method_decorator(never_cache, name='dispatch')
class ShopView(generic.View):
    def get(self, request):
        products = Product.objects.filter(status='active').select_related('category', 'brand') \
                         .prefetch_related('reviews').annotate(avg_rate=Avg('reviews__rating'))
        
        paginator = Paginator(products, 12)  # 12 products per page
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj
        }
        return render(request, 'store/shop.html', context)

# =========================================================
# AJAX: GET PRODUCT VARIANT PRICE / STOCK / IMAGE
# =========================================================
@method_decorator(csrf_exempt, name='dispatch')
class GetVariantsView(generic.View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        color_id = request.POST.get('color_id')
        size_id = request.POST.get('size_id')

        variant = ProductVariant.objects.filter(
            product_id=product_id,
            color_id=color_id or None,
            size_id=size_id or None,
            status='active'
        ).first()

        if variant:
            data = {
                'variant_price': float(variant.variant_price),
                'available_stock': variant.available_stock,
                'image_url': variant.image.url if variant.image else ''
            }
        else:
            data = {'variant_price': None, 'available_stock': 0, 'image_url': ''}

        return JsonResponse(data)


