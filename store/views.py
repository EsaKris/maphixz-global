from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from decimal import Decimal
from django.contrib.auth.decorators import user_passes_test
from .admin_views import is_admin
import urllib.parse
from .models import Category, Product, Order, OrderItem, Cart, CartItem, ProductImage
from .utils import get_cart, add_to_cart_session, remove_from_cart_session, get_whatsapp_url

def home(request):
    """Homepage with featured products"""
    featured_products = Product.objects.filter(featured=True)[:6]
    categories = Category.objects.all()[:4]
    return render(request, 'store/home.html', {
        'featured_products': featured_products,
        'categories': categories
    })

def product_list(request):
    """Display all products with filtering and search"""
    products = Product.objects.all()
    categories = Category.objects.all()

    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    else:
        category = None

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )

    # Filter by stock status
    stock_filter = request.GET.get('stock')
    if stock_filter:
        products = products.filter(stock_status=stock_filter)

    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories,
        'current_category': category,
        'search_query': search_query,
        'stock_filter': stock_filter
    })

def product_detail(request, slug):
    """Display individual product details"""
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]

    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products
    })

def category_products(request, slug):
    """Display products in a specific category"""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)

    return render(request, 'store/category_products.html', {
        'category': category,
        'products': products
    })

def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id)

    if not product.is_available:
        messages.error(request, f'{product.name} is not available.')
        return redirect('store:product_detail', slug=product.slug)

    cart = get_cart(request)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f'{product.name} added to cart!')
    return redirect('store:product_detail', slug=product.slug)

def cart_detail(request):
    """Display cart contents"""
    cart = get_cart(request)
    cart_items = cart.items.all()

    return render(request, 'store/cart.html', {
        'cart': cart,
        'cart_items': cart_items
    })

def update_cart(request, item_id):
    """Update cart item quantity"""
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            cart = get_cart(request)
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, 'Cart updated successfully!')
            else:
                cart_item.delete()
                messages.success(request, 'Item removed from cart!')

        except ValueError:
            messages.error(request, 'Invalid quantity.')

    return redirect('store:cart')

def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart = get_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    product_name = cart_item.product.name
    cart_item.delete()

    messages.success(request, f'{product_name} removed from cart!')
    return redirect('store:cart')

def checkout(request):
    """Handle checkout process"""
    cart = get_cart(request)
    cart_items = cart.items.all()

    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('store:product_list')

    if request.method == 'POST':
        # Calculate subtotal
        subtotal = sum(item.product.price * item.quantity for item in cart_items)

        # Process checkout form
        order = Order(
            customer_name=request.POST['customer_name'],
            customer_email=request.POST['customer_email'],
            customer_phone=request.POST['customer_phone'],
            delivery_address=request.POST['delivery_address'],
            delivery_city=request.POST['delivery_city'],
            delivery_method=request.POST['delivery_method'],
            delivery_notes=request.POST.get('delivery_notes', ''),
            payment_method=request.POST['payment_method'],
            total_amount=cart.total_price,
            subtotal=subtotal,  
        )
        order.save()

        # Create order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )

        # Clear cart
        cart_items.delete()

        # Handle payment method
        if order.payment_method == 'whatsapp':
            whatsapp_url = get_whatsapp_url(order)
            # Auto-confirm WhatsApp orders for demo purposes
            confirm_whatsapp_payment(order)
            return redirect(whatsapp_url)
        else:
            # Create Stripe checkout session
            import stripe
            from django.conf import settings
            stripe.api_key = settings.STRIPE_SECRET_KEY
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(order.total_amount * 100),  # Convert to cents
                        'product_data': {
                            'name': f'Order #{order.id}',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(
                    reverse('store:payment_success', kwargs={'order_id': order.id})
                ),
                cancel_url=request.build_absolute_uri(
                    reverse('store:payment_cancel', kwargs={'order_id': order.id})
                ),
                client_reference_id=str(order.id),
            )
            return redirect(checkout_session.url)

    return render(request, 'store/checkout.html', {
        'cart': cart,
        'cart_items': cart_items
    })

def order_confirmation(request, order_id):
    """Display order confirmation"""
    order = get_object_or_404(Order, id=order_id)
    whatsapp_url = request.GET.get('whatsapp_url')

    return render(request, 'store/order_confirmation.html', {
        'order': order,
        'whatsapp_url': whatsapp_url
    })

# AJAX Views
@require_POST
def ajax_add_to_cart(request, product_id):
    """AJAX endpoint to add product to cart"""
    product = get_object_or_404(Product, id=product_id)

    if not product.is_available:
        return JsonResponse({
            'success': False,
            'message': f'{product.name} is not available.'
        })

    cart = get_cart(request)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return JsonResponse({
        'success': True,
        'message': f'{product.name} added to cart!',
        'cart_count': cart.total_items
    })

@require_POST
def ajax_update_cart(request, item_id):
    """AJAX endpoint to update cart item quantity"""
    try:
        quantity = int(request.POST.get('quantity', 1))
        cart = get_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()

            return JsonResponse({
                'success': True,
                'message': 'Cart updated successfully!',
                'subtotal': float(cart_item.subtotal),
                'cart_total': float(cart.total_price),
                'cart_count': cart.total_items
            })
        else:
            cart_item.delete()
            return JsonResponse({
                'success': True,
                'message': 'Item removed from cart!',
                'cart_total': float(cart.total_price),
                'cart_count': cart.total_items
            })

    except ValueError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid quantity.'
        })

def search_products(request):
    """AJAX search endpoint"""
    query = request.GET.get('q', '')
    if len(query) >= 2:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )[:10]

        results = [{
            'id': str(product.id),
            'name': product.name,
            'price': float(product.price),
            'url': product.get_absolute_url(),
            'image': product.image.url if product.image else None
        } for product in products]

        return JsonResponse({'results': results})

    return JsonResponse({'results': []})
def payment_success(request, order_id):
    """Handle successful payment"""
    order = get_object_or_404(Order, id=order_id)
    order.status = 'confirmed'
    order.save()
    messages.success(request, 'Payment successful! Thank you for your order.')
    return render(request, 'store/order_confirmation.html', {'order': order})

def payment_cancel(request, order_id):
    """Handle cancelled payment"""
    order = get_object_or_404(Order, id=order_id)
    order.status = 'cancelled'
    order.save()
    messages.error(request, 'Payment was cancelled.')
    return redirect('store:checkout')

def confirm_whatsapp_payment(order):
    """Confirms payment for WhatsApp orders."""
    order.status = 'confirmed'
    order.save()
    
def contact(request):
    return render(request, 'store/contact.html')

# store/views.py
from django.shortcuts import render

def shipping_policy(request):
    return render(request, 'store/shipping_policy.html')

def returns_exchanges(request):
    return render(request, 'store/returns_exchanges.html')

def faq(request):
    return render(request, 'store/faq.html')

def hair_care_guide(request):
    return render(request, 'store/hair_care_guide.html')

def privacy_policy(request):
    return render(request, 'store/privacy_policy.html')

def terms_of_service(request):
    return render(request, 'store/terms_of_service.html')

def services_view(request):
    # You can add context data to pass to the template
    context = {
        'services': [
            {
                'name': 'Laptop Sales',
                'description': 'We sell brand new and refurbished laptops from top brands.',
                'icon': 'fa-laptop'  # Example Font Awesome icon
            },
            {
                'name': 'Laptop Repairs',
                'description': 'Professional repair services for all laptop models and issues.',
                'icon': 'fa-tools'
            },
            {
                'name': 'Data Recovery',
                'description': 'Recover your important files from damaged laptops.',
                'icon': 'fa-hdd'
            }
        ]
    }
    return render(request, 'store/services.html', context)

@user_passes_test(is_admin, login_url='store:admin_login')
def admin_set_cover_image(request, image_id):
    """Set an image as the cover image"""
    image = get_object_or_404(ProductImage, id=image_id)
    product_id = image.product.id
    
    if request.method == 'POST':
        # This will automatically unset any other cover images due to the model's save() method
        image.is_cover = True
        image.save()
        messages.success(request, "Cover image updated successfully!")
    
    return redirect('store:admin_edit_product', product_id=product_id)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    # Try to get featured image, else first image, else None
    cover_image = product.images.filter(is_featured=True).first()
    if not cover_image:
        cover_image = product.images.first()
    # ...other context...
    return render(request, 'store/product_detail.html', {
        'product': product,
        'cover_image': cover_image,
        # ...other context...
    })