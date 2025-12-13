from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Avg, Q
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
        sliders = active_sliders.filter(
            Q(slider_type='slider') |
            Q(slider_type='feature')
        )

        feature_sliders = active_sliders.filter(Q(slider_type='feature'))[:4]
        add_sliders = active_sliders.filter(Q(slider_type='add'))[:2]
        promo_sliders = active_sliders.filter(Q(slider_type='promotion'))[:3]
        
        acceptance_payments = AcceptancePayment.objects.filter(status='active')[:4]
        # featured brands
        brands = Brand.objects.filter(status='active', is_featured=True)
        # featured categories
        cates = Category.objects.filter(status='active', children__isnull=True, is_featured=True)[:3]
        # top deals products
        top_deals = list(Product.objects.filter(
            status='active', discount_percent__gt=0, is_deadline=True, deadline__gte=timezone.now()
        ).select_related('category', 'brand').prefetch_related('reviews') \
         .annotate(avg_rate=Avg('reviews__rating', filter=Q(reviews__status='active'))).order_by('-discount_percent', 'deadline')[:6]
        )
        first_top_deal = top_deals[0] if top_deals else None
        # featured products
        featured_products = Product.objects.filter(
            status='active', is_featured=True
        ).select_related('category', 'brand').prefetch_related('reviews') \
         .annotate(avg_rate=Avg('reviews__rating', filter=Q(reviews__status='active')))[:5]


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
    def get(self, request, slug, id):
        # Main product fetch
        product = get_object_or_404(
            Product.objects.select_related('category', 'brand')
                .prefetch_related('reviews', 'variants__color', 'variants__size', 'images')
                .annotate(avg_rate=Avg('reviews__rating', filter=Q(reviews__status='active'))),
            slug=slug,
            id=id,
            status='active'
        )

        # Default variant (first one) fetch
        variant = product.variants.first()  # if multiple variants first default 

        # Related products
        related_products = Product.objects.filter(
            category=product.category,
            status='active'
        ).exclude(id=product.id).select_related('category', 'brand') \
         .prefetch_related('reviews').annotate(avg_rate=Avg('reviews__rating', filter=Q(reviews__status='active')))[:4]

        context = {
            'product': product,
            'variant': variant,   
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
                         .prefetch_related('reviews').annotate(avg_rate=Avg('reviews__rating', filter=Q(reviews__status='active')))
        
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


