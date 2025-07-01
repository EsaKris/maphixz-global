from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import uuid

class Category(models.Model):
    TYPE_CHOICES = [
        ('laptop', 'Laptop'),
        ('accessory', 'Accessory'),
        ('part', 'Component/Part'),
        ('service', 'Repair Service'),
    ]
    
    ICON_CHOICES = [
        ('laptop', 'fa-laptop'),
        ('desktop', 'fa-desktop'),
        ('mobile', 'fa-mobile-alt'),
        ('cpu', 'fa-microchip'),
        ('ram', 'fa-memory'),
        ('storage', 'fa-hdd'),
        ('repair', 'fa-tools'),
        ('accessory', 'fa-keyboard'),
    ]

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category_type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES, 
        default='laptop',
        help_text="Type of products in this category"
    )
    icon = models.CharField(
        max_length=20, 
        choices=ICON_CHOICES, 
        default='laptop',
        help_text="Icon to represent this category"
    )
    image = models.ImageField(
        upload_to='categories/', 
        blank=True, 
        null=True,
        help_text="Category banner image"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Featured categories appear on homepage"
    )
    warranty_months = models.PositiveIntegerField(
        default=12,
        help_text="Default warranty period for products in this category (months)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
        indexes = [
            models.Index(fields=['category_type']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:category_products', kwargs={'slug': self.slug})

    @property
    def icon_class(self):
        """Returns the Font Awesome icon class for this category"""
        return dict(self.ICON_CHOICES).get(self.icon, 'fa-laptop')

    @property
    def display_warranty(self):
        """Formats the warranty period for display"""
        if self.warranty_months >= 12:
            years = self.warranty_months // 12
            return f"{years} Year{'s' if years > 1 else ''} Warranty"
        return f"{self.warranty_months} Month Warranty"

    def get_products_count(self):
        """Returns count of active products in this category"""
        return self.products.filter(stock_status='available').count()


class Product(models.Model):
    STOCK_CHOICES = [
        ('available', 'Available'),
        ('out_of_stock', 'Out of Stock'),
        ('sold_out', 'Sold Out'),
    ]
    
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('NGN', 'Nigerian Naira'),
        ('GBP', 'British Pound'),
    ]

    # Core Product Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    brand = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    
    # Pricing Information
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    
    # Inventory Information
    stock_status = models.CharField(max_length=20, choices=STOCK_CHOICES, default='available')
    stock_quantity = models.PositiveIntegerField(default=0)
    
    # Technical Specifications
    processor = models.CharField(max_length=100, blank=True)
    ram = models.CharField(max_length=50, blank=True)
    storage = models.CharField(max_length=100, blank=True)
    graphics = models.CharField(max_length=100, blank=True)
    display = models.CharField(max_length=100, blank=True)
    dimensions = models.CharField(max_length=100, blank=True)
    weight = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)
    operating_system = models.CharField(max_length=100, blank=True, null=True)
    
    # Warranty & Condition
    warranty = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Warranty period in months (uses category default if empty)"
    )
    is_refurbished = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)
    
    # Media
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    video = models.FileField(upload_to='products/videos/', blank=True, null=True)
    
    # Flags & Metadata
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stock_status']),
            models.Index(fields=['featured']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['brand']),
            models.Index(fields=['is_refurbished']),
        ]

    def __str__(self):
        return f"{self.brand} {self.name}" if self.brand else self.name

    def get_absolute_url(self):
        return reverse('store:product_detail', kwargs={'slug': self.slug})

    @property
    def is_available(self):
        return self.stock_status == 'available'

    @property
    def stock_badge_class(self):
        return {
            'available': 'success',
            'out_of_stock': 'warning', 
            'sold_out': 'danger'
        }.get(self.stock_status, 'secondary')

    @property
    def effective_warranty(self):
        """Returns the product's warranty or falls back to category default"""
        return self.warranty if self.warranty is not None else self.category.warranty_months

    @property
    def display_warranty(self):
        """Formats the warranty period for display"""
        months = self.effective_warranty
        if months >= 12:
            years = months // 12
            return f"{years} Year{'s' if years > 1 else ''} Warranty"
        return f"{months} Month Warranty"

    @property
    def discount_percentage(self):
        """Calculates discount percentage if discount price exists"""
        if self.discount_price:
            return round((1 - (self.discount_price / self.price)) * 100)
        return None

    @property
    def cover_image(self):
        # Try to get featured image, else first image, else None
        featured = self.images.filter(is_featured=True).first()
        if featured:
            return featured
        return self.images.first() or None

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/images/')
    caption = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', 'created_at']

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, related_name='specifications', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=200)
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name}: {self.value}"


class Order(models.Model):
    PAYMENT_CHOICES = [
        ('online', 'Online Payment'),
        ('whatsapp', 'WhatsApp Payment'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash on Delivery'),
    ]

    DELIVERY_CHOICES = [
        ('standard', 'Standard Delivery (3-5 days)'),
        ('express', 'Express Delivery (1-2 days)'),
        ('pickup', 'Pickup from Store'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    # Order Identification
    id = models.CharField(max_length=8, primary_key=True, editable=False)
    
    # Customer Information
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    
    # Delivery Information  
    delivery_address = models.TextField()
    delivery_city = models.CharField(max_length=100)
    delivery_state = models.CharField(max_length=100, blank=True)
    delivery_postal_code = models.CharField(max_length=20, blank=True)
    delivery_country = models.CharField(max_length=100, default='Nigeria')
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES)
    delivery_notes = models.TextField(blank=True)
    
    # Order Details
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Product.CURRENCY_CHOICES, default='USD')
    
    # Status Flags
    is_payment_confirmed = models.BooleanField(default=False)
    payment_confirmation_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['customer_email']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} - {self.customer_name}"

    @property
    def status_badge_class(self):
        return {
            'pending': 'warning',
            'confirmed': 'info',
            'processing': 'primary',
            'shipped': 'success',
            'delivered': 'success',
            'cancelled': 'danger'
        }.get(self.status, 'secondary')

    def get_absolute_url(self):
        return reverse('store:order_detail', kwargs={'order_id': self.id})


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    warranty_months = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('order', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        return self.quantity * self.price

    @property
    def display_warranty(self):
        """Returns the warranty period for this order item"""
        months = self.warranty_months if self.warranty_months else self.product.effective_warranty
        if months >= 12:
            years = months // 12
            return f"{years} Year{'s' if years > 1 else ''}"
        return f"{months} Month{'s' if months > 1 else ''}"


class Cart(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'product')
        indexes = [
            models.Index(fields=['product']),
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        return self.quantity * self.product.price


class WarrantyRegistration(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('void', 'Void'),
    ]

    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE, related_name='warranty')
    registration_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Warranty Registrations"
        ordering = ['-registration_date']

    def __str__(self):
        return f"Warranty for {self.order_item.product.name}"

    @property
    def is_active(self):
        return self.status == 'active'


class RepairService(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('hardware', 'Hardware Repair'),
        ('software', 'Software Issue'),
        ('upgrade', 'Upgrade Service'),
        ('diagnostic', 'Diagnostic'),
    ]

    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('diagnosed', 'Diagnosed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_completion = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Repair #{self.id} - {self.get_service_type_display()}"

    @property
    def is_covered_by_warranty(self):
        """Check if this repair might be covered under warranty"""
        if self.product and hasattr(self.product, 'warranty'):
            return True
        return False