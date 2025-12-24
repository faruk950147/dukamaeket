from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Sum, F
import logging

from cart.models import Cart
from store.models import Product, ProductVariant

logger = logging.getLogger('project')

# ==================================
# Add To Cart
# ==================================
from django.views import generic
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

@method_decorator(never_cache, name='dispatch')
class AddToCartView(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('sign-in')

    def post(self, request):
        # fetch data from POST request then validate
        product_slug = request.POST.get("product_slug")
        product_id = request.POST.get("product_id")
        select_color = request.POST.get("color")       # optional
        select_size = request.POST.get("size")         # optional
        quantity = int(request.POST.get("quantity", 1))

        if quantity < 1:
            return JsonResponse({"status": "error", "message": "Quantity must be at least 1."})

        # Fetch active product
        product = get_object_or_404(Product, slug=product_slug, id=product_id, status='active')
        product.refresh_from_db(fields=["available_stock"])

        # Resolve variant safely
        variant_qs = ProductVariant.objects.filter(product=product)
        if select_color:
            variant_qs = variant_qs.filter(color_id=select_color)
        if select_size:
            variant_qs = variant_qs.filter(size_id=select_size)
            
        # There should be at most one variant matching the criteria
        variant = None
        if variant_qs.count() > 0:
            variant = variant_qs[0]
        elif select_color or select_size:
            return JsonResponse({"status": "error", "message": "Selected variant does not exist."})

        # Determine max stock
        if variant:
            max_stock = variant.available_stock
            if max_stock <= 0:
                return JsonResponse({"status": "error", "message": "Selected variant is out of stock."})
        else:
            max_stock = product.available_stock
            if max_stock <= 0:
                return JsonResponse({"status": "error", "message": "Product is out of stock."})
        
        return JsonResponse({
            "status": "success",
            "message": "Product can be added to cart.",
            "product_title": product.title,
            "available_stock": max_stock
        })

# ================================
# Cart Detail Page
# ================================
@method_decorator(never_cache, name='dispatch')
class CartDetailView(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('sign-in')

    def get(self, request):
        pass


# ================================
# Increase/Decrease Quantity
# ================================
@method_decorator(never_cache, name="dispatch")
class QuantityIncDec(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('sign-in')

    def post(self, request):
        pass


# ================================
# Remove From Cart
# ================================
@method_decorator(never_cache, name='dispatch')
class CartRemoveView(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('sign-in')

    def post(self, request):
        pass