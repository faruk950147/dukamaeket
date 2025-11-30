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
        # Sliders
        sliders = Slider.objects.filter(status='active')[:4]
        feature_sliders = Slider.objects.filter(status='active', slider_type='feature')[:4]
        add_sliders = Slider.objects.filter(status='active', slider_type='add')[:2]
        promo_sliders = Slider.objects.filter(status='active', slider_type='promotion')[:3]

        # Acceptance Payments
        acceptance_payments = AcceptancePayment.objects.filter(status='active')[:4]

        # Featured Brands
        brands = Brand.objects.filter(status='active', is_featured=True)

        # Featured Categories
        cates = Category.objects.filter(status='active', children__isnull=True, is_featured=True).distinct()[:3]

        # Top Deals
        top_deals_qs = Product.objects.filter(
            status='active',
            is_deadline=True,
            deadline__gte=timezone.now()
        ).select_related('category', 'brand').prefetch_related('reviews') \
         .annotate(avg_rate=Avg('reviews__rating')).order_by('deadline')[:6]
        top_deals = list(top_deals_qs)
        first_top_deal = top_deals[0] if top_deals else None

        # Featured Products
        featured_products_qs = Product.objects.filter(
            status='active',
            is_featured=True
        ).select_related('category', 'brand').prefetch_related('reviews') \
         .annotate(avg_rate=Avg('reviews__rating'))[:5]
        featured_products = list(featured_products_qs)

        user = request.user.username if request.user.is_authenticated else 'Anonymous'
        logger.debug(
            f"User {user} visited Home page. "
            f"Sliders: {sliders.count()}, Feature Sliders: {feature_sliders.count()}, "
            f"Add Sliders: {add_sliders.count()}, Promo Sliders: {promo_sliders.count()}, "
            f"AcceptancePayments: {acceptance_payments.count()}, Categories: {cates.count()}, "
            f"Brands: {brands.count()}, Top Deals: {len(top_deals)}, Featured Products: {len(featured_products)}"
        )

        context = {
            'sliders': sliders,
            'feature_sliders': feature_sliders,
            'add_sliders': add_sliders,
            'promo_sliders': promo_sliders,
            'acceptance_payments': acceptance_payments,
            'cates': cates,
            'top_deals': top_deals,
            'featured_products': featured_products,
            'first_top_deal': first_top_deal,
            'brands': brands
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
                   .prefetch_related('reviews', 'variants__color', 'variants__size', 'images'),
            id=id,
            status='active'
        )

        related_products_qs = Product.objects.filter(
            category=product.category,
            status='active'
        ).exclude(id=product.id).select_related('category', 'brand') \
         .prefetch_related('reviews').annotate(avg_rate=Avg('reviews__rating'))[:4]
        related_products = list(related_products_qs)

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
        products_qs = Product.objects.filter(status='active').select_related('category', 'brand') \
                         .prefetch_related('reviews')
        paginator = Paginator(products_qs, 12)  # 12 products per page
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context = {
            'products': page_obj.object_list,
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
