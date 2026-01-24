from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import F, Sum
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from store.models import Product, ProductVariant
from cart.models import Coupon, Cart, Wishlist
import logging

logger = logging.getLogger('project')
# ================================
# Add to Cart View
# ===============================
@method_decorator(never_cache, name='dispatch')
class AddToCartView(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('sign-in')

    def post(self, request):
        # Fetch POST data safely
        product_slug = request.POST.get("product_slug")
        product_id = request.POST.get("product_id")
        variant_id = request.POST.get("variant_id")
        quantity = int(request.POST.get("quantity", "1"))

        if not product_slug or not product_id:
            return JsonResponse({"status": "error", "message": "Invalid product data."})
        if quantity < 1:
            return JsonResponse({"status": "error", "message": "Quantity must be at least 1."})
        
        with transaction.atomic():
            print("product slug :", product_slug, "product id", product_id, "variant id", variant_id)
 


            return JsonResponse({
                "status": "success",
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