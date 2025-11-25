from django.shortcuts import render
from django.views import generic
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.utils import timezone
from store.models import (
    Category,
    Brand,
    Product,
    ImageGallery,
    Color,
    Size,
    ProductVariant,
    Review,
    Advancement,
    Slider
)
# Create your views here.

@method_decorator(never_cache, name='dispatch')
class HomeView(generic.View):
    def get(self, request):
        context = {
            'sliders': Slider.objects.filter(status='active')[:4],
            'features_sliders': Advancement.objects.filter(status='active', advancement_type='feature')[:4],
            'top_deals': Product.objects.filter(status='active', is_deadline='active', deadline__gte=timezone.now())[:5],
            'featured_products': Product.objects.filter(status='active', is_featured='active')[:5],
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