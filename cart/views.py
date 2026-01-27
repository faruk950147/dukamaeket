from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
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
        product_slug = request.POST.get("product_slug")
        product_id = request.POST.get("product_id")
        variant_id = request.POST.get("variant_id")
        quantity = int(request.POST.get("quantity", "1"))

        if not product_slug or not product_id:
            return JsonResponse({"status": "error", "message": "Invalid product data."})

        if quantity < 1:
            return JsonResponse({"status": "error", "message": "Quantity must be at least 1."})

        with transaction.atomic():

            # Product
            product = get_object_or_404(
                Product,
                slug=product_slug,
                id=product_id,
                status='active'
            )
            product.refresh_from_db(fields=["available_stock"])

            # Variant resolve
            variant = None

            if product.variant != 'none':
                if not variant_id:
                    return JsonResponse({
                        "status": "error",
                        "message": "Please select a product variant."
                    })

                variant = get_object_or_404(
                    ProductVariant,
                    id=variant_id,
                    product=product,
                    status='active'
                )
                variant.refresh_from_db(fields=["available_stock"])

            # Stock check
            max_stock = variant.available_stock if variant else product.available_stock

            if max_stock <= 0:
                return JsonResponse({
                    "status": "error",
                    "message": "Selected variant is out of stock." if variant else "Product is out of stock."
                })

            # Cart merge
            cart_qs = Cart.objects.filter(
                user=request.user,
                product=product,
                variant=variant,
                paid=False
            )
            cart_list = list(cart_qs)
            existing_cart_item = cart_list[0] if cart_list else None

            if existing_cart_item:
                new_quantity = existing_cart_item.quantity + quantity
                if new_quantity > max_stock:
                    return JsonResponse({
                        "status": "error",
                        "message": f"Cannot exceed available stock ({max_stock})."
                    })
                existing_cart_item.quantity = new_quantity
                existing_cart_item.save()
                final_quantity = new_quantity
                message = "Product quantity updated in cart successfully."
            else:
                Cart.objects.create(
                    user=request.user,
                    product=product,
                    variant=variant,
                    quantity=quantity,
                    paid=False
                )
                final_quantity = quantity
                message = "Product added to cart successfully."

            # Cart summary
            cart_items = Cart.objects.filter(
                user=request.user,
                paid=False
            ).select_related("product", "variant", "variant__color", "variant__size")

            cart_count = cart_items.count()
            total_price = sum(
                item.quantity * item.stored_unit_price for item in cart_items
            )

            # Image resolve
            image_url = "/media/defaults/default.jpg"

            if variant and variant.image_url:
                image_url = variant.image_url
            elif product.images.exists():
                image_url = product.images.first().image.url


            return JsonResponse({
                "status": "success",
                "message": message,
                "product_title": product.title,
                "sale_price": str(product.sale_price),
                "old_price": str(product.old_price),
                "quantity": final_quantity,
                "available_stock": max_stock,
                "cart_count": cart_count,
                "total_price": str(total_price),
                "image_url": image_url
            })

@method_decorator(never_cache, name='dispatch')
class CartDetailView(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('sign-in')
    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user, paid=False).select_related('product','variant')
        total_price = sum([item.subtotal for item in cart_items])
        return render(request, "cart/cart-detail.html", {
            "cart_items": cart_items,
            "total_price": total_price
        })

@method_decorator(never_cache, name='dispatch')
class QuantityIncDec(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('sign-in')

    def post(self, request):
        cart_id = request.POST.get("cart_id")
        action = request.POST.get("action")

        cart_item = get_object_or_404(Cart, id=cart_id, user=request.user, paid=False)

        max_stock = cart_item.variant.available_stock if cart_item.variant else cart_item.product.available_stock

        if action == "inc":
            if cart_item.quantity < max_stock:
                cart_item.quantity += 1
                message = "increased"
            else:
                message = "max stock reached"

        elif action == "dec":
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                message = "decreased"
            else:
                message = "minimum quantity is 1"
        else:
            message = "invalid action"

        cart_item.save()

        cart_items = Cart.objects.filter(user=request.user, paid=False)
        cart_total = sum(item.subtotal for item in cart_items)

        return JsonResponse({
            "status": "success",
            "message": message,
            "quantity": cart_item.quantity,
            "item_total": float(cart_item.subtotal),
            "cart_total": float(cart_total)
        })

@method_decorator(never_cache, name='dispatch')
class CartRemoveView(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('sign-in')

    def post(self, request):
        cart_id = request.POST.get("cart_id")

        cart_item = get_object_or_404(Cart, id=cart_id, user=request.user, paid=False)
        cart_item.delete()

        cart_items = Cart.objects.filter(user=request.user, paid=False)

        total_price = sum(item.subtotal for item in cart_items)
        cart_count = cart_items.count()

        return JsonResponse({
            "status": "success",
            "message": "Item removed from cart",
            "cart_count": cart_count,
            "total_price": float(total_price),
            "cart_empty": cart_count == 0
        })
