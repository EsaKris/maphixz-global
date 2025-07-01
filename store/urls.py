from django.urls import path
from . import views, admin_views

app_name = 'store'

urlpatterns = [
    # Main store pages
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('contact/', views.contact, name='contact'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
     path('services/', views.services_view, name='services'),
    
    # Cart functionality

    path('payment/success/<str:order_id>/', views.payment_success, name='payment_success'),
    path('payment/cancel/<str:order_id>/', views.payment_cancel, name='payment_cancel'),

    path('cart/', views.cart_detail, name='cart'),
    path('add-to-cart/<uuid:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout and orders
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<str:order_id>/', views.order_confirmation, name='order_confirmation'),
    
    # AJAX endpoints
    path('ajax/add-to-cart/<uuid:product_id>/', views.ajax_add_to_cart, name='ajax_add_to_cart'),
    path('ajax/update-cart/<int:item_id>/', views.ajax_update_cart, name='ajax_update_cart'),
    path('ajax/search/', views.search_products, name='search_products'),
    
    # Custom Admin Panel
    path('maphixz-admin/', admin_views.admin_login_view, name='admin_login'),
    path('maphixz-admin/logout/', admin_views.admin_logout_view, name='admin_logout'),
    path('maphixz-admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('maphixz-admin/products/', admin_views.admin_products, name='admin_products'),
    path('maphixz-admin/products/add/', admin_views.admin_add_product, name='admin_add_product'),
    path('maphixz-admin/products/edit/<uuid:product_id>/', admin_views.admin_edit_product, name='admin_edit_product'),
    path('maphixz-admin/products/delete/<uuid:product_id>/', admin_views.admin_delete_product, name='admin_delete_product'),
    path('maphixz-admin/customers/', admin_views.admin_customers, name='admin_customers'),
    path('maphixz-admin/set-cover-image/<int:image_id>/', views.admin_set_cover_image, name='admin_set_cover_image'),
    path('maphixz-admin/products/image/delete/<int:image_id>/', admin_views.admin_delete_product_image, name='admin_delete_product_image'),
    path('maphixz-admin/orders/', admin_views.admin_orders, name='admin_orders'),
    path('maphixz-admin/customers/<str:customer_email>/', admin_views.admin_customer_detail, name='admin_customer_detail'),
    path('maphixz-admin/orders/<str:order_id>/', admin_views.admin_order_detail, name='admin_order_detail'),
    path('maphixz-admin/categories/', admin_views.admin_categories, name='admin_categories'),
    
    path('maphixz-admin/settings/', admin_views.admin_settings, name='admin_settings'),
    path('maphixz-admin/settings/shipping/', admin_views.admin_settings, name='admin_shipping_settings'),

    path('shipping-policy/', views.shipping_policy, name='shipping_policy'),
    path('returns-exchanges/', views.returns_exchanges, name='returns_exchanges'),
    path('faq/', views.faq, name='faq'),
    path('hair-care-guide/', views.hair_care_guide, name='hair_care_guide'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),

]