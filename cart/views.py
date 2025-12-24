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
        select_color = request.POST.get("color")
        select_size = request.POST.get("size")
        quantity = request.POST.get("quantity", "1")

        if not product_slug or not product_id:
            return JsonResponse({"status": "error", "message": "Invalid product data."})
        if quantity < 1:
            return JsonResponse({"status": "error", "message": "Quantity must be at least 1."})
        
        with transaction.atomic():
            # Fetch product
            product = get_object_or_404(Product, slug=product_slug, id=product_id, status='active')
            product.refresh_from_db(fields=["available_stock"])

            # Fetch variant if applicable
            variant_qs = ProductVariant.objects.filter(product=product)
            if select_color:
                variant_qs = variant_qs.filter(color_id=select_color)
            if select_size:
                variant_qs = variant_qs.filter(size_id=select_size)

            variant = variant_qs[0] if variant_qs else None
            if (select_color or select_size) and not variant:
                return JsonResponse({"status": "error", "message": "Selected variant does not exist."})

            # Determine max stock
            max_stock = variant.available_stock if variant else product.available_stock
            if max_stock <= 0:
                msg = "Selected variant is out of stock." if variant else "Product is out of stock."
                return JsonResponse({"status": "error", "message": msg})

            # Check existing cart
            cart_qs = Cart.objects.filter(user=request.user, product=product, variant=variant, paid=False)
            cart_list = list(cart_qs)
            existing_cart_item = cart_list[0] if cart_list else None

            if existing_cart_item:
                new_quantity = existing_cart_item.quantity + quantity
                if new_quantity > max_stock:
                    return JsonResponse({"status": "error", "message": f"Cannot exceed available stock ({max_stock})."})
                existing_cart_item.quantity = new_quantity
                existing_cart_item.save()
                final_quantity = new_quantity
                message = "Product quantity updated in cart successfully."
            else:
                Cart.objects.create(user=request.user, product=product, variant=variant, quantity=quantity, paid=False)
                final_quantity = quantity
                message = "Product added to cart successfully."

            # Cart summary
            cart_items = Cart.objects.filter(user=request.user, paid=False).select_related(
                "product", "variant", "variant__color", "variant__size"
            )
            cart_count = cart_items.count()
            total_price = sum(item.quantity * item.product.sale_price for item in cart_items)

            # Image selection
            image_url = ""
            if variant and getattr(variant, "image", None):
                image_url = variant.image.url
            elif hasattr(product, 'images') and product.images.first():
                image_url = product.images.first().image.url
            else:
                image_url = '/media/defaults/default.jpg'

            return JsonResponse({
                "status": "success",
                "message": message,
                "product_title": product.title,
                "sale_price": str(product.sale_price),
                "old_price": str(product.old_price),
                "quantity": final_quantity,
                "available_stock": max_stock,
                "cart_count": cart_count,
                "total_price": total_price,
                "image_url": image_url
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