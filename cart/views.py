from decimal import Decimal, ROUND_HALF_UP
from django.views import generic
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from store.models import Product, ProductVariant
from cart.models import Cart


@method_decorator(never_cache, name='dispatch')
class AddToCartView(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('sign-in')

    def post(self, request):
        user = request.user

        product_slug = request.POST.get("product_slug")
        product_id = request.POST.get("product_id")
        select_color = request.POST.get("color")
        select_size = request.POST.get("size")
        quantity_raw = request.POST.get("quantity", "1")

        # -------------------------
        # Basic validation
        # -------------------------
        if not product_slug or not product_id:
            return JsonResponse({
                "status": "error",
                "message": "Invalid product data."
            })

        try:
            quantity = int(quantity_raw)
        except (TypeError, ValueError):
            return JsonResponse({
                "status": "error",
                "message": "Invalid quantity."
            })

        if quantity < 1:
            return JsonResponse({
                "status": "error",
                "message": "Quantity must be at least 1."
            })

        with transaction.atomic():

            # -------------------------
            # Fetch product (locked)
            # -------------------------
            product = get_object_or_404(
                Product.objects.select_for_update(),
                id=product_id,
                slug=product_slug,
                status='active'
            )

            # -------------------------
            # Variant selection (STRICT)
            # -------------------------
            variant_qs = ProductVariant.objects.filter(
                product=product,
                status='active'
            )

            if select_color and select_size:
                variant_qs = variant_qs.filter(
                    color_id=select_color,
                    size_id=select_size
                )
            elif select_color:
                variant_qs = variant_qs.filter(
                    color_id=select_color,
                    size__isnull=True
                )
            elif select_size:
                variant_qs = variant_qs.filter(
                    size_id=select_size,
                    color__isnull=True
                )
            else:
                variant_qs = variant_qs.filter(is_default=True)

            variant = variant_qs.first()

            # If user selected something but variant not found
            if (select_color or select_size) and not variant:
                return JsonResponse({
                    "status": "error",
                    "message": "Selected variant does not exist."
                })

            # -------------------------
            # Stock check
            # -------------------------
            if variant:
                max_stock = variant.available_stock
                if max_stock <= 0:
                    return JsonResponse({
                        "status": "error",
                        "message": "Selected variant is out of stock."
                    })
            else:
                max_stock = product.available_stock
                if max_stock <= 0:
                    return JsonResponse({
                        "status": "error",
                        "message": "Product is out of stock."
                    })

            # -------------------------
            # Cart merge / create
            # -------------------------
            cart_item = Cart.objects.filter(
                user=user,
                product=product,
                variant=variant,
                paid=False
            ).first()

            if cart_item:
                new_quantity = cart_item.quantity + quantity
                if new_quantity > max_stock:
                    return JsonResponse({
                        "status": "error",
                        "message": f"Cannot exceed available stock ({max_stock})."
                    })
                cart_item.quantity = new_quantity
                cart_item.save()
                final_quantity = new_quantity
                message = "Product quantity updated in cart successfully."
            else:
                unit_price = (
                    variant.variant_price
                    if variant and variant.variant_price > 0
                    else product.sale_price
                )

                Cart.objects.create(
                    user=user,
                    product=product,
                    variant=variant,
                    quantity=quantity,
                    stored_unit_price=unit_price,
                    paid=False
                )
                final_quantity = quantity
                message = "Product added to cart successfully."

            # -------------------------
            # Cart summary
            # -------------------------
            cart_items = Cart.objects.filter(
                user=user,
                paid=False
            )

            cart_count = cart_items.count()
            total_price = sum(
                item.subtotal for item in cart_items
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            # -------------------------
            # Image selection
            # -------------------------
            if variant and variant.image:
                image_url = variant.image.url
            elif product.images.exists():
                image_url = product.images.first().image.url
            else:
                image_url = "/media/defaults/default.jpg"

            # -------------------------
            # Variant display (FINAL LOGIC)
            # -------------------------
            if not variant:
                variant_display = "-"
            else:
                size = variant.size.title if variant.size else None
                color = variant.color.title if variant.color else None

                if size and color:
                    variant_display = f"{size} - {color}"
                else:
                    variant_display = size or color

            # -------------------------
            # Response
            # -------------------------
            unit_price = (
                variant.variant_price
                if variant and variant.variant_price > 0
                else product.sale_price
            )

            return JsonResponse({
                "status": "success",
                "message": message,
                "product_title": product.title,
                "variant_display": variant_display,
                "sale_price": str(unit_price),
                "old_price": str(product.old_price),
                "quantity": final_quantity,
                "available_stock": max_stock,
                "cart_count": cart_count,
                "total_price": str(total_price),
                "image_url": image_url,
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