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

from .models import Cart
from store.models import Product

logger = logging.getLogger('project')

# Create your views here.
# Add To Cart
@method_decorator(never_cache, name='dispatch')
class AddToCartView(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('sign-in')
    def post(self, request):
        product_id = request.POST.get("product-id")
        product_slug = request.POST.get("product-slug")
        quantity = int(request.POST.get("quantity", 1))
        print(f"Add to cart request: product_id={product_id}, product_slug={product_slug}, quantity={quantity}")


        return JsonResponse({
            "status": "success",
            "message": "Product added to cart successfully.",
        })

# Cart Detail Page
@method_decorator(never_cache, name='dispatch')
class CartDetailView(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('sign-in')

    def get(self, request):
        pass

# Increase/Decrease Quantity
@method_decorator(never_cache, name="dispatch")
class QuantityIncDec(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('sign-in')

    def post(self, request):
        pass

# Remove From Cart
@method_decorator(never_cache, name='dispatch')
class CartRemoveView(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('sign-in')

    def post(self, request):
        pass