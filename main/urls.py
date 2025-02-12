from django.urls import path, include
from . import api
from rest_framework import routers

router = routers.DefaultRouter()
router.register('address', api.CustomerAddressViewset)
router.register('productrating', api.ProductRatingViewset)

urlpatterns = [
    # Vendor related views
    path('vendors/', api.VendorList.as_view()),  # List all vendors
    path('vendor/<uuid:pk>/', api.VendorDetail.as_view()),  # Detailed view of a single vendor by ID
    path('vendor/register/', api.vendor_register, name='vendor_register'),  # Vendor registration
    path('vendor/login/', api.vendor_login, name='vendor_login'),  # Vendor login
    path('vendor/<uuid:pk>/orderitems', api.VendorOrderItemsList.as_view()),  # List order items for a specific vendor
    path('vendor/<uuid:pk>/customers', api.VendorList.as_view()),  # List customers of a specific vendor
    path('vendor/dashboard/<uuid:pk>/', api.vendor_dashboard, name='vendor_dashboard'),  # Vendor dashboard
    path('vendor-change-password/<uuid:user_id>/', api.change_password, name='change_password', kwargs={'user_type': 'vendor'}),
    path('vendor/forget-password/', api.vendor_forget_password, name='vendor_forget_password'),  # Vendor forget password
    path('vendor/verify-vendor/<uuid:vendor_id>/', api.verify_vendor_via_otp, name='verify_vendor_via_otp'),  # Verify vendor via OTP
    # path('request-activation/', api.request_activation, name='request_activation'),
    # path('activate/<str:otp_digit>/', api.activate_vendor, name='activate_vendor'),
    
    # Customer related views
    path('customer-change-password/<uuid:customer_id>/', api.change_password, name='change_password'),  # Customer change password
    path('customers/', api.CustomerList.as_view()),  # List all customers
    path('customer/<uuid:pk>/', api.CustomerDetail.as_view()),  # Detailed view of a single customer by ID
    path('customer/verify-customer/<uuid:customer_id>/', api.verify_custome_via_otp, name='verify_custome_via_otp'),  # Verify customer via OTP
    path('customer/forget-password/', api.customer_forget_password, name='customer_forget_password'),  # Customer forget password
    path('customer/login/', api.Customer_login, name='Customer_login'),  # Customer login
    path('customer/register/', api.Customer_register, name='Customer_register'),  # Customer registration
    path('customer/<uuid:pk>/orderitems', api.CustomerOrderItemsList.as_view()),  # List order items for a specific customer
    path('customer/<uuid:pk>/address-list/', api.CustomerAddressList.as_view()),  # List addresses of a specific customer
    path('mark-default-address/<uuid:pk>/', api.mark_default_address, name='mark_default_address'),  # Mark an address as default
    path('customer/dashboard/<uuid:pk>/', api.customer_dashboard, name='customer_dashboard'),  # Customer dashboard
    
    # Product related views
    path('products/', api.ProductList.as_view(), name='product-list'),
    path('products/<uuid:pk>/', api.ProductList.as_view(), name='product-list'),
    path('related-products/<uuid:pk>/', api.RelatedProductList.as_view()),
    path('products-imgs/', api.ProductImgList.as_view()),  # List all product images
    path('products-imgs/<uuid:product_id>/', api.ProductImgDetail.as_view()),  # Detailed view of product images by product ID
    path('products-img/<uuid:pk>/', api.ProductImgmuiltiDetail.as_view()),  # Detailed view of a single product image by ID
    path('product/<uuid:pk>/', api.ProductDetail.as_view()),  # Detailed view of a single product by ID
    path('categories/', api.CategoryList.as_view()),  # List all product categories
    path('category/<uuid:pk>/', api.CategoryDetail.as_view()),  # Detailed view of a single category by ID

    # Order related views
    path('orders/', api.OrderList.as_view()),  # List all orders
    path('order/<uuid:pk>/', api.OrderDetail.as_view()),  # Detailed view of a single order by ID
    path('order-status-modify/<uuid:pk>/', api.OrderItemStatusModify.as_view()),  # Modify the status of an order item
    path('orderitems/', api.OrderItemsList.as_view()),  # List all order items
    path('orderitem/<uuid:pk>/', api.OrderItemsDetail.as_view()),  # Detailed view of a single order item by ID
    path('update-order-status/<uuid:order_id>/', api.update_order_status),  # Update the status of an order
    path('new-orders/<uuid:order_id>/<uuid:vendor_id>/', api.get_order_items, name='get_order_items'),
    
    # User related views
    path('user/<uuid:pk>/', api.UserDetail.as_view()),  # Detailed view of a single user by ID

    # Search view
    path('search/', api.search, name='search'),  # Search functionality
]

# Include the router's URLs
urlpatterns += router.urls  # Include routes for CustomerAddressViewset and ProductRatingViewset
