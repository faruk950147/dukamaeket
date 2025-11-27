from django.shortcuts import render, get_object_or_404
from django.views import generic
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
        sliders = Slider.objects.filter(status='active')[:4]
        feature_sliders = Slider.objects.filter(status='active', slider_type='feature')[:4]
        acceptance_payments = AcceptancePayment.objects.filter(status='active')[:4]

        # Featured Categories
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
        ).annotate(avg_rate=Avg('reviews__rate'))[:5]

        # Featured Products
        featured_products = Product.objects.filter(
            status='active',
            is_featured=True
        ).annotate(avg_rate=Avg('reviews__rate'))[:5] # related new field add this method

        # Logging
        logger.info(
            f"User {request.user if request.user.is_authenticated else 'Anonymous'} visited Home page. "
            f"Sliders: {sliders.count()}, Feature Sliders: {feature_sliders.count()}, "
            f"AcceptancePayments: {acceptance_payments.count()}, Categories: {cates.count()}, "
            f"Top Deals: {top_deals.count()}, Featured Products: {featured_products.count()}"
        )

        context = {
            'sliders': sliders,
            'features_sliders': feature_sliders,
            'acceptance_payments': acceptance_payments,
            'cates': cates,
            'top_deals': top_deals,
            'featured_products': featured_products,
        }
        return render(request, 'store/home.html', context)


@method_decorator(never_cache, name='dispatch')
class ProductDetailView(generic.View):
    def get(self, request):
        return render(request, 'store/product-detail.html')
 
@method_decorator(never_cache, name='dispatch')
class ShopView(generic.View):
    def get(self, request):
        return render(request, 'store/shop.html')