from decimal import Decimal, ROUND_HALF_UP
from email.mime import message
from django.views import generic
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth.mixins import LoginRequiredMixin
from store.models import Product, ProductVariant, Color, Size
from cart.models import Cart

# ================================
# Add to Cart View
# ================================
@method_decorator(never_cache, name='dispatch')
class AddToCartView(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('sign-in')

    def post(self, request):
        user = request.user
        # Get POST data
        product_slug = request.POST.get("product_slug")
        product_id = request.POST.get("product_id")
        select_color = request.POST.get("color")
        select_size = request.POST.get("size")
        quantity = int(request.POST.get("quantity", "1"))
        
        if quantity < 1:
            return JsonResponse({"status": "error", "message": "Invalid quantity."}, status=400)
        
        with transaction.atomic():
            # Fetch product object
            product = get_object_or_404(
                Product.objects.select_for_update(),
                slug=product_slug,
                id=product_id,
            status='active'
            )
            # Fetch product variant object if applicable
            variant = None
            if select_color or select_size:
                color = Color.objects.get(id=select_color) if select_color else None
                size = Size.objects.get(id=select_size) if select_size else None

                variant = get_object_or_404(
                    ProductVariant.objects.select_for_update(),
                    product=product,
                    color=color,
                    size=size
                )
                
            # Check stock availability
            available_stock = variant.available_stock if variant else product.available_stock
            if quantity > available_stock:
                return JsonResponse({
                    "status": "error",
                    "message": f"Only {available_stock} unit(s) available."
                }, status=400)
            return JsonResponse({"status": "success", "message": "Product added to cart."})


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