from django.conf import settings
from .models import Cart, CartItem
import urllib.parse

def get_cart(request):
    """Get or create cart for current session"""
    if not request.session.session_key:
        request.session.create()

    cart, created = Cart.objects.get_or_create(
        session_key=request.session.session_key
    )
    return cart

def add_to_cart_session(request, product, quantity=1):
    """Add product to session cart (legacy function for compatibility)"""
    cart = get_cart(request)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return cart_item

def remove_from_cart_session(request, product):
    """Remove product from session cart (legacy function for compatibility)"""
    cart = get_cart(request)
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.delete()
        return True
    except CartItem.DoesNotExist:
        return False

def get_whatsapp_url(order):
    whatsapp_number = "+2349155775787"
    message = f"Hello! I would like to complete my order #{order.id}.\n"
    message += f"Total Amount: {order.currency} {order.total_amount}\n"
    message += f"Items:\n"
    
    for item in order.items.all():
        message += f"- {item.quantity}x {item.product.name}\n"
    
    message += "\nPlease provide payment instructions."
    
    return f"https://wa.me/{whatsapp_number}?text={urllib.parse.quote(message)}"

def confirm_whatsapp_payment(order):
    order.is_payment_confirmed = True
    order.status = 'confirmed'
    order.save()
    # Format the order details for WhatsApp
    message = f"*New Order #{order.id}*\n\n"
    message += f"Customer: {order.customer_name}\n"
    message += "\n*Order Items:*\n"

    for item in order.items.all():
        message += f"- {item.quantity}x {item.product.name} @ ${item.price}\n"

    message += f"\n*Total Amount:* ${order.total_amount}\n"
    message += f"*Delivery Address:* {order.delivery_address}, {order.delivery_city}\n"
    message += f"*Delivery Method:* {order.get_delivery_method_display()}"

    # WhatsApp business number - replace with your number
    whatsapp_number = "1234567890"

    # Encode the message for URL
    encoded_message = urllib.parse.quote(message)
    return f"https://wa.me/{whatsapp_number}?text={encoded_message}"

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:.2f}"