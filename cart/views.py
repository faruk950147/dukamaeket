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
from decimal import Decimal
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

        # Basic validation
        if not product_slug or not product_id:
            return JsonResponse({"status": "error", "message": "Invalid product data."})
        if quantity < 1:
            return JsonResponse({"status": "error", "message": "Quantity must be at least 1."})

        with transaction.atomic():
            # Fetch product with row lock to avoid overselling
            product = get_object_or_404(Product.objects.select_for_update(), slug=product_slug, id=product_id, status='active')

            # Variant resolve
            variant = None
            if product.variant != 'none':
                if not variant_id:
                    return JsonResponse({"status": "error", "message": "Please select a product variant."})
                variant = get_object_or_404(ProductVariant.objects.select_for_update(), id=variant_id, product=product, status='active')

            # Determine available stock
            max_stock = variant.available_stock if variant else product.available_stock
            if max_stock <= 0:
                return JsonResponse({
                    "status": "error",
                    "message": "Selected variant is out of stock." if variant else "Product is out of stock."
                })

            # Determine unit price (stored_unit_price)
            unit_price = variant.variant_price if variant and variant.variant_price > 0 else product.sale_price

            # Merge with existing cart if exists
            cart_item = Cart.objects.filter(user=request.user, product=product, variant=variant, paid=False).first()

            if cart_item:
                new_quantity = cart_item.quantity + quantity
                if new_quantity > max_stock:
                    return JsonResponse({
                        "status": "error",
                        "message": f"Cannot exceed available stock ({max_stock})."
                    })
                cart_item.quantity = new_quantity
                cart_item.stored_unit_price = unit_price
                cart_item.save()
                final_quantity = new_quantity
                message = "Product quantity updated in cart successfully."
            else:
                Cart.objects.create(
                    user=request.user,
                    product=product,
                    variant=variant,
                    quantity=quantity,
                    stored_unit_price=unit_price,
                    paid=False
                )
                final_quantity = quantity
                message = "Product added to cart successfully."

            # Cart summary
            cart_summary = Cart.objects.filter(user=request.user, paid=False).aggregate(
                total_price=Sum(F('quantity') * F('stored_unit_price')),
                cart_count=Sum(F('quantity'))
            )
            cart_count = cart_summary['cart_count'] or 0
            total_price = Decimal(cart_summary['total_price'] or 0).quantize(Decimal('0.01'))

            # Image resolve
            image_url = None
            if variant and variant.image_url:
                image_url = variant.image_url
            elif product.images.exists():
                image_url = product.images.first().image.url
            else:
                image_url = "/media/defaults/default.jpg"

            # JSON response
            return JsonResponse({
                "status": "success",
                "message": message,
                "product_title": variant.title if variant else product.title,
                "unit_price": str(unit_price),
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
                message = "Quantity increased"
            else:
                return JsonResponse({'status': 'error', 'message': 'Maximum stock reached'})

        elif action == "dec":
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                message = "Quantity decreased"
            else:
                return JsonResponse({'status': 'error', 'message': 'Minimum quantity is 1'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid action'})

        # Save after changing quantity
        cart_item.save()

        # Recalculate cart total
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
        if not cart_id:
            return JsonResponse({"status": "error", "message": "No cart ID provided"})

        # Get the cart item
        cart_item = get_object_or_404(Cart, id=cart_id, user=request.user, paid=False)
        cart_item.delete()

        # Recalculate cart info
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