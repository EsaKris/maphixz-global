from .utils import get_cart

def cart_context(request):
    """Add cart information to all templates"""
    cart = get_cart(request)
    return {
        'cart_count': cart.total_items,
        'cart_total': cart.total_price,
    }