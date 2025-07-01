from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Order, OrderItem, Cart, CartItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']
    
    def subtotal(self, obj):
        if obj.pk:
            return f"${obj.subtotal:.2f}"
        return "-"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock_status', 'featured', 'created_at']
    list_filter = ['category', 'stock_status', 'featured', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['stock_status', 'featured', 'price']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock_status', 'featured')
        }),
        ('Media', {
            'fields': ('image',)
        }),
    )
    
    def stock_status_badge(self, obj):
        colors = {
            'available': 'green',
            'out_of_stock': 'orange',
            'sold_out': 'red'
        }
        color = colors.get(obj.stock_status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_stock_status_display()
        )
    stock_status_badge.short_description = 'Stock Status'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'customer_email', 'total_amount', 
                   'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'delivery_method', 'created_at']
    search_fields = ['id', 'customer_name', 'customer_email', 'customer_phone']
    list_editable = ['status']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'status', 'total_amount', 'payment_method')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Delivery Information', {
            'fields': ('delivery_address', 'delivery_city', 'delivery_method', 'delivery_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'confirmed': 'blue',
            'processing': 'purple',
            'shipped': 'green',
            'delivered': 'darkgreen',
            'cancelled': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['subtotal']
    
    def subtotal(self, obj):
        if obj.pk:
            return f"${obj.subtotal:.2f}"
        return "-"

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'total_items', 'total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['session_key']
    readonly_fields = ['session_key', 'total_items', 'total_price']
    inlines = [CartItemInline]

# Customize admin site
admin.site.site_header = 'Maphixz Global Administration'
admin.site.site_title = 'Maphixz Global  Admin'
admin.site.index_title = 'Welcome to Maphixz Global Administration'