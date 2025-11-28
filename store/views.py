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
        # Main Sliders
        sliders = Slider.objects.filter(status='active', slider_type='slider')[:4]

        # Feature Sliders
        features_sliders = Slider.objects.filter(status='active', slider_type='feature')[:4]

        # Add Sliders
        add_sliders = Slider.objects.filter(status='active', slider_type='add')[:4]

        # Acceptance Payments
        acceptance_payments = AcceptancePayment.objects.filter(status='active')[:4]

        # Featured Categories (leaf nodes only)
        cates = Category.objects.filter(
            status='active',
            children__isnull=True,
            is_featured=True
        ).distinct()[:3]

        # Top Deals (deadline active)
        top_deals = Product.objects.filter(
            status='active',
            is_deadline=True,
            deadline__gte=timezone.now()
        ).select_related('category', 'brand').annotate(avg_rate=Avg('reviews__rate')).order_by('deadline')[:5]
        first_top_deal = top_deals.first()

        # Featured Products
        featured_products = Product.objects.filter(
            status='active',
            is_featured=True
        ).select_related('category', 'brand').annotate(avg_rate=Avg('reviews__rate'))[:5]

        # Logging
        logger.info(
            f"User {request.user if request.user.is_authenticated else 'Anonymous'} visited Home page. "
            f"Sliders: {sliders.count()}, Feature Sliders: {features_sliders.count()}, "
            f"Add Sliders: {add_sliders.count()}, AcceptancePayments: {acceptance_payments.count()}, "
            f"Categories: {cates.count()}, Top Deals: {top_deals.count()}, Featured Products: {featured_products.count()}"
        )

        # Context
        context = {
            'sliders': sliders,
            'features_sliders': features_sliders,
            'add_sliders': add_sliders,
            'acceptance_payments': acceptance_payments,
            'cates': cates,
            'top_deals': top_deals,
            'first_top_deal': first_top_deal,
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