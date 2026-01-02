from decimal import ROUND_HALF_UP, Decimal
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
class AddToCartView(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('sign-in')

    def post(self, request):
        user = request.user
        product_slug = request.POST.get("product_slug")
        product_id = request.POST.get("product_id")
        select_color = request.POST.get("color")
        select_size = request.POST.get("size")
        quantity = int(request.POST.get("quantity", "1"))

        if not product_slug or not product_id:
            return JsonResponse({"status": "error", "message": "Invalid product data."})
        if quantity < 1:
            return JsonResponse({"status": "error", "message": "Quantity must be at least 1."})

        with transaction.atomic():
            # Fetch product
            product = get_object_or_404(Product, slug=product_slug, id=product_id, status='active')
            product.refresh_from_db(fields=["available_stock"])

            # -------------------------------
            # Fetch variant strictly based on selection
            # -------------------------------
            variant_qs = ProductVariant.objects.filter(product=product)

            if select_color and select_size:
                variant_qs = variant_qs.filter(color_id=select_color, size_id=select_size)
            elif select_color:
                variant_qs = variant_qs.filter(color_id=select_color, size__isnull=True)
            elif select_size:
                variant_qs = variant_qs.filter(size_id=select_size, color__isnull=True)
            else:
                variant_qs = variant_qs.filter(is_default=True)

            variant = variant_qs.first() if variant_qs.exists() else None

            # Check if variant exists
            if (select_color or select_size) and not variant:
                return JsonResponse({"status": "error", "message": "Selected variant does not exist."})

            # Determine available stock
            max_stock = variant.available_stock if variant else product.available_stock
            if max_stock <= 0:
                msg = "Selected variant is out of stock." if variant else "Product is out of stock."
                return JsonResponse({"status": "error", "message": msg})

            # Check if item already in cart
            cart_qs = Cart.objects.filter(user=user, product=product, variant=variant, paid=False)
            cart_item = cart_qs.first() if cart_qs.exists() else None

            if cart_item:
                # Update quantity
                new_quantity = cart_item.quantity + quantity
                if new_quantity > max_stock:
                    return JsonResponse({"status": "error", "message": f"Cannot exceed available stock ({max_stock})."})
                cart_item.quantity = new_quantity
                cart_item.save()
                final_quantity = new_quantity
                message = "Product quantity updated in cart successfully."
            else:
                # Create new cart item
                Cart.objects.create(
                    user=user,
                    product=product,
                    variant=variant,
                    quantity=quantity,
                    stored_unit_price=variant.variant_price if variant and variant.variant_price > 0 else product.sale_price,
                    paid=False
                )
                final_quantity = quantity
                message = "Product added to cart successfully."

            # Cart summary
            cart_items = Cart.objects.filter(user=user, paid=False).select_related(
                "product", "variant", "variant__color", "variant__size"
            )

            cart_count = cart_items.count()
            total_price = sum(item.subtotal for item in cart_items)

            # Image selection
            image_url = ""
            if variant and getattr(variant, "image", None):
                image_url = variant.image.url
            elif product.images.exists():
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
                "total_price": total_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
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