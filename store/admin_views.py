from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Max
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Product, Category, Order, OrderItem, Cart, CartItem, ProductImage
from decimal import Decimal

def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and (user.is_superuser or user.is_staff)

def admin_login_view(request):
    """Custom admin login view"""
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('store:admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user and is_admin(user):
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('store:admin_dashboard')  # This is already correct, but we'll ensure it's the main redirect
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')
    
    return render(request, 'admin/login.html')

def admin_logout_view(request):
    """Admin logout"""
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('store:admin_login')

@user_passes_test(is_admin, login_url='store:admin_login')
def admin_dashboard(request):
    """Admin dashboard with analytics"""
    # Get date range for analytics
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    
    # Order status counts
    order_status_counts = Order.objects.values('status').annotate(count=Count('status'))
    
    # Convert to individual variables with default 0 values
    completed_orders = next(
        (item['count'] for item in order_status_counts if item['status'] == 'completed'), 
        0
    )
    processing_orders = next(
        (item['count'] for item in order_status_counts if item['status'] == 'processing'), 
        0
    )
    pending_orders = next(
        (item['count'] for item in order_status_counts if item['status'] == 'pending'), 
        0
    )
    cancelled_orders = next(
        (item['count'] for item in order_status_counts if item['status'] == 'cancelled'), 
        0
    )
    
    # Total orders (sum of all statuses)
    total_orders = completed_orders + processing_orders + pending_orders + cancelled_orders
    
    # Product analytics
    total_products = Product.objects.count()
    low_stock = Product.objects.filter(stock_status='out_of_stock').count()
    
    # Revenue analytics
    total_revenue = Order.objects.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0')
    
    monthly_revenue = Order.objects.filter(
        created_at__gte=last_30_days
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0')
    
    # Recent orders
    recent_orders = Order.objects.select_related('customer').order_by('-created_at')[:5]
    
    # Popular products
    popular_products = Product.objects.annotate(
        order_count=Count('orderitem')
    ).order_by('-order_count')[:5]
    
    context = {
        # Order status data
        'completed_orders': completed_orders,
        'processing_orders': processing_orders,
        'pending_orders': pending_orders,
        'cancelled_orders': cancelled_orders,
        'total_orders': total_orders,
        
        # Product data
        'total_products': total_products,
        'low_stock': low_stock,
        
        # Revenue data
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        
        # Lists
        'recent_orders': recent_orders,
        'popular_products': popular_products,
    }
    
    return render(request, 'admin/dashboard.html', context)

@user_passes_test(is_admin, login_url='store:admin_login')
def admin_products(request):
    """Products management"""
    search = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    
    products = Product.objects.all()
    
    if search:
        products = products.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search)
        )
    
    if category_filter:
        products = products.filter(category__slug=category_filter)
    
    products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'search': search,
        'category_filter': category_filter,
    }
    
    return render(request, 'admin/products.html', context)

@user_passes_test(is_admin, login_url='store:admin_login')
def admin_orders(request):
    """Orders management"""
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    orders = Order.objects.all()
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if search:
        orders = orders.filter(
            Q(id__icontains=search) |
            Q(customer_name__icontains=search) |
            Q(customer_email__icontains=search)
        )
    
    orders = orders.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 15)
    page = request.GET.get('page')
    orders = paginator.get_page(page)
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'search': search,
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'admin/orders.html', context)

@user_passes_test(is_admin, login_url='store:admin_login')
def admin_order_detail(request, order_id):
    """Order detail view"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {order.get_status_display()}')
            return redirect('store:admin_order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'admin/order_detail.html', context)

@user_passes_test(is_admin, login_url='store:admin_login')
def admin_add_product(request):
    """Add new product"""
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock_status = request.POST.get('stock_status')
        featured = request.POST.get('featured') == 'on'
        image = request.FILES.get('image')
        # Technical specs
        processor = request.POST.get('processor')
        ram = request.POST.get('ram')
        storage = request.POST.get('storage')
        graphics = request.POST.get('graphics')
        display = request.POST.get('display')
        operating_system = request.POST.get('operating_system')
        # Add other fields as needed

        try:
            category = Category.objects.get(id=category_id)
            from django.utils.text import slugify
            slug = slugify(name)
            original_slug = slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1

            product = Product.objects.create(
                name=name,
                slug=slug,
                category=category,
                description=description,
                price=Decimal(price),
                stock_status=stock_status,
                featured=featured,
                image=image,
                processor=processor,
                ram=ram,
                storage=storage,
                graphics=graphics,
                display=display,
                operating_system=operating_system,
                # Add other fields here
            )

            
            # Handle multiple images (up to 5)
            if request.FILES.getlist('images'):
                images = request.FILES.getlist('images')[:5]
                for i, img in enumerate(images):
                    ProductImage.objects.create(
                        product=product, 
                        image=img,
                        is_cover=(i == 0)  # First image is the cover
                    )
                if len(request.FILES.getlist('images')) > 5:
                    messages.warning(request, "Only 5 images were uploaded (max allowed per product).")

            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('store:admin_products')
        except Exception as e:
            messages.error(request, f'Error creating product: {str(e)}')

    categories = Category.objects.all()
    context = {
        'categories': categories,
        'stock_choices': Product.STOCK_CHOICES,
    }
    return render(request, 'admin/add_product.html', context)

@user_passes_test(is_admin, login_url='store:admin_login')
def admin_edit_product(request, product_id):
    """Edit product"""
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.brand = request.POST.get('brand')
        product.condition = request.POST.get('condition')
        product.sku = request.POST.get('sku')
        product.serial_number = request.POST.get('serial_number')
        product.battery_life = request.POST.get('battery_life')
        product.warranty = request.POST.get('warranty')
        product.description = request.POST.get('description')
        product.price = Decimal(request.POST.get('price'))
        product.stock_status = request.POST.get('stock_status')
        product.featured = request.POST.get('featured') == 'on'
        product.processor = request.POST.get('processor')
        product.ram = request.POST.get('ram')
        product.storage = request.POST.get('storage')
        product.graphics = request.POST.get('graphics')
        product.display = request.POST.get('display')
        product.operating_system = request.POST.get('operating_system')

        category_id = request.POST.get('category')
        if category_id:
            product.category = Category.objects.get(id=category_id)

        if request.FILES.getlist('images'):
            existing_count = product.images.count()
            allowed = max(0, 5 - existing_count)
            images = request.FILES.getlist('images')[:allowed]
            for img in images:
                ProductImage.objects.create(product=product, image=img)
            if len(request.FILES.getlist('images')) > allowed:
                messages.warning(request, f'Only {allowed} more images allowed (max 5 per product).')

        product.save()
        messages.success(request, f'Product "{product.name}" updated successfully!')
        return redirect('store:admin_products')

    categories = Category.objects.all()
    context = {
        'product': product,
        'categories': categories,
        'stock_choices': Product.STOCK_CHOICES,
    }
    return render(request, 'admin/edit_product.html', context)

@user_passes_test(is_admin, login_url='store:admin_login')
def admin_delete_product(request, product_id):
    """Delete product"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
    
    return redirect('store:admin_products')

@user_passes_test(is_admin, login_url='store:admin_login')
def admin_categories(request):
    """Categories management"""
    categories = Category.objects.annotate(
        product_count=Count('products')
    ).order_by('name')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'admin/categories.html', context)

@user_passes_test(is_admin, login_url='store:admin_login')
def admin_customers(request):
    """Admin: List all customers (aggregated from orders)"""
    customers = (
        Order.objects
        .exclude(customer_email='')
        .values('customer_email', 'customer_name', 'customer_phone')
        .annotate(
            purchase_count=Count('id', filter=Q(status='purchase')),
            repair_count=Count('id', filter=Q(status='repair')),
            total_spent=Sum('total_amount', filter=Q(status='purchase')),
            repair_spent=Sum('total_amount', filter=Q(status='repair')),
            last_purchase=Max('created_at', filter=Q(status='purchase')),
            last_repair=Max('created_at', filter=Q(status='repair'))
        )
        .order_by('-last_purchase')
    )

    # Add search and filtering
    search_query = request.GET.get('q')
    if search_query:
        customers = customers.filter(
            Q(customer_name__icontains=search_query) |
            Q(customer_email__icontains=search_query) |
            Q(customer_phone__icontains=search_query)
        )

    customer_type = request.GET.get('customer_type')
    if customer_type == 'buyer':
        customers = customers.filter(purchase_count__gt=0)
    elif customer_type == 'repair':
        customers = customers.filter(repair_count__gt=0)
    elif customer_type == 'both':
        customers = customers.filter(purchase_count__gt=0, repair_count__gt=0)

    paginator = Paginator(customers, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin/customers.html', {'customers': page_obj})


@user_passes_test(is_admin, login_url='store:admin_login')
def admin_customer_detail(request, customer_email):
    """Show all orders for a specific customer by email"""
    orders = Order.objects.filter(customer_email=customer_email).order_by('-created_at')
    purchases = orders.filter(status='purchase')
    repairs = orders.filter(status='repair')

    # Get customer info from the first order, if available
    customer_info = orders.first()

    context = {
        'customer_email': customer_email,
        'customer_info': customer_info,
        'orders': orders,
        'purchases': purchases,
        'repairs': repairs,
        'total_purchases': purchases.count(),
        'total_repairs': repairs.count(),
        'total_spent': purchases.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'repair_spent': repairs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
    }
    return render(request, 'admin/customer_detail.html', context)

@staff_member_required
def admin_settings(request):
    """Admin: Settings page (placeholder)"""
    return render(request, 'admin/settings.html')

def admin_shipping_settings(request):
    # Your logic here
    return render(request, 'admin/shipping_settings.html')

@user_passes_test(is_admin, login_url='store:admin_login')
def admin_delete_product_image(request, image_id):
    """Delete a product image (AJAX or POST)"""
    image = get_object_or_404(ProductImage, id=image_id)
    product_id = image.product.id
    if request.method == 'POST':
        image.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        messages.success(request, "Image deleted successfully.")
    return redirect('store:admin_edit_product', product_id=product_id)


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