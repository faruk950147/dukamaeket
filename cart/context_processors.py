from cart.models import Cart


def cart_context(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user, paid=False).select_related('product','variant')[:3]
        cart_count = cart_items.count()
        total_price = sum([item.subtotal for item in cart_items])
        return {'cart_items': cart_items, 'total_price': total_price, 'cart_count': cart_count}
    return {'cart_items': [], 'cart_count': 0, 'total_price': 0}