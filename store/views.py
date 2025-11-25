from django.shortcuts import render
from django.views import generic
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.utils import timezone
from store.models import (
    AcceptancePayment,
    Category,
    Brand,
    Product,
    ImageGallery,
    Color,
    Size,
    ProductVariant,
    Review,
    Advancement,
    AcceptancePayment,
    Slider
)
# Create your views here.

@method_decorator(never_cache, name='dispatch')
class HomeView(generic.View):
    def get(self, request):
        # Sliders
        sliders = Slider.objects.filter(status='active')
        # banner
        banners = Advancement.objects.filter(status='active', advancement_type='banner')
        # Top Deals
        top_deals = Product.objects.filter(
            status='active', 
            is_timeline='active', 
            deadline__gte=timezone.now()).order_by('-discount_percent')[:5]
        # Featured Products
        featured_products = Product.objects.filter(
            advancements__advancement_type='feature',
            advancements__status='active',
            status='active'
        ).distinct()[:5]
        context = {
            'sliders': sliders,
            'banners': banners,
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