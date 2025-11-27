from django.shortcuts import render
from django.views import generic
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.utils import timezone
from store.models import (
    Category,
    Brand,
    Product,
    Slider,
    AcceptancePayment
)
# Create your views here.
import logging
logger = logging.getLogger('project')
@method_decorator(never_cache, name='dispatch')
class HomeView(generic.View):

    def get(self, request):
        # main slider
        sliders = Slider.objects.filter(status='active')[:4]
        # featured slider
        feature_sliders = Slider.objects.filter(status='active', slider_type='feature')[:4]
        # available payments methods
        acceptance_payments = AcceptancePayment.objects.filter(status='active')[:4]

        # featured Categories
        cates = Category.objects.filter(
            status='active',
            children__isnull=True,
            is_featured=True
        ).distinct()[:3]
        # top deals products
        top_deals = Product.objects.filter(
            status='active',
            is_deadline=True,
            deadline__gte=timezone.now()
        )[:5]
        # featured products
        featured_products = Product.objects.filter(
            status='active',
            is_featured=True
        )[:5]

        # Logging information
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