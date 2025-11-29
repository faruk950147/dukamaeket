from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.utils import timezone
from django.db.models import Avg
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
        add_sliders = Slider.objects.filter(status='active', slider_type='add')[:4]
        promo_sliders = Slider.objects.filter(status='active', slider_type='promotion')[:3]

        # Acceptance Payments
        acceptance_payments = AcceptancePayment.objects.filter(status='active')[:4]

        # Brands
        brands = Brand.objects.filter(status='active', is_featured=True)

        # Featured Categories (leaf categories)
        cates = Category.objects.filter(
            status='active',
            children__isnull=True,
            is_featured=True
        ).distinct()[:3]

        # Top Deals
        top_deals = Product.objects.filter(
            status='active',
            is_deadline=True,
            deadline__gte=timezone.now()
        ).prefetch_related('reviews').annotate(avg_rate=Avg('reviews__rating')).order_by('deadline')[:5]
        first_top_deal = top_deals.first()

        # Featured Products
        featured_products = Product.objects.filter(
            status='active',
            is_featured=True
        ).prefetch_related('reviews').annotate(avg_rate=Avg('reviews__rating'))[:5]

        # Logging
        user = self.request.user if self.request.user.is_authenticated else 'Anonymous'
        logger.info(
            f"User {user} visited Home page. "
            f"Sliders: {sliders.count()}, Feature Sliders: {feature_sliders.count()}, "
            f"Add Sliders: {add_sliders.count()}, Promotion Sliders: {promo_sliders.count()}, "
            f"AcceptancePayments: {acceptance_payments.count()}, Categories: {cates.count()}, Brands: {brands.count()}, "
            f"Top Deals: {top_deals.count()}, Featured Products: {featured_products.count()}"
        )


        context = {
            'sliders': sliders,
            'features_sliders': feature_sliders,
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
    
@method_decorator(never_cache, name='dispatch')
class ProductDetailView(generic.View):
    def get(self, request, id):

        # Product + Reviews prefetch (optimized)
        product = get_object_or_404(Product, id=id, status='active')

        # Related Products + Reviews prefetch
        related_products = Product.objects.filter(
            category=product.category,
            status='active'
        ).prefetch_related('reviews').annotate(
            avg_rate=Avg('reviews__rating')
        ).exclude(id=product.id)[:4]

        context = {
            'product': product,
            'related_products': related_products
        }
        return render(request, 'store/product-detail.html', context)

 
@method_decorator(never_cache, name='dispatch')
class ShopView(generic.View):
    def get(self, request):
        products = Product.objects.filter(status='active')
        context = {
            'products': products
        }
        return render(request, 'store/shop.html', context)