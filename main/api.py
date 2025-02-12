from rest_framework import generics, permissions, pagination, viewsets
from . import serializers
from . import models
import json
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.db.models import Count
from .models import User
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from random import randint
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db.models import Sum,F
# from .models import Vendor, VendorActivationRequest

class VendorList(generics.ListCreateAPIView):
    queryset = models.Vendor.objects.all()
    serializer_class = serializers.VendorSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if 'fetch_limit' in self.request.GET:
            limit = int(self.request.GET['fetch_limit'])
            qs = qs.annotate(download=Count('product')).order_by('-download', '-id')
            qs = qs[:limit]
        return qs

class VendorDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Vendor.objects.all()
    serializer_class = serializers.VendorDetailSerializer

class VendorOrderItemsList(generics.ListAPIView):
    queryset = models.OrderItems.objects.all()
    serializer_class = serializers.OrderItemListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        vendor_id = self.kwargs['pk']
        qs = qs.filter(product__vendor__id=vendor_id)
        return qs

@csrf_exempt
def change_password(request, user_type, user_id):
    if request.method == 'POST':
        password = request.POST.get('password')
        try:
            if user_type == 'vendor':
                user_instance = models.Vendor.objects.get(id=user_id).user
            else:
                user_instance = models.Customer.objects.get(id=user_id).user
            user_instance.password = make_password(password)
            user_instance.save()
            return JsonResponse({'bool': True, 'msg': 'Password has been changed'})
        except (models.Vendor.DoesNotExist, models.Customer.DoesNotExist):
            return JsonResponse({'bool': False, 'msg': 'User does not exist'})
    return JsonResponse({'bool': False, 'msg': 'Invalid request method'}, status=400)



class ProductList(generics.ListCreateAPIView):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        qs = super().get_queryset()

        # Check if 'pk' exists in self.kwargs
        vendor_id = self.kwargs.get('pk')
        if vendor_id:
            qs = qs.filter(vendor__id=vendor_id)

        # Handle 'category' filter
        category_id = self.request.GET.get('category')
        if category_id:
            try:
                category = models.ProductCategory.objects.get(id=category_id)
                qs = qs.filter(category=category)
            except models.ProductCategory.DoesNotExist:
                pass

        # Handle 'fetch_limit' filter
        fetch_limit = self.request.GET.get('fetch_limit')
        if fetch_limit:
            try:
                limit = int(fetch_limit)
                qs = qs[:limit]
            except ValueError:
                pass

        # Handle 'popular' filter
        popular = self.request.GET.get('popular')
        if popular:
            try:
                limit = int(popular)
                qs = qs.order_by('-download', '-id')[:limit]
            except ValueError:
                pass

        return qs

class ProductImgList(generics.ListCreateAPIView):
    queryset = models.ProductImages.objects.all()
    serializer_class = serializers.ProductImageSerializer

class ProductImgDetail(generics.ListCreateAPIView):
    queryset = models.ProductImages.objects.all()
    serializer_class = serializers.ProductImageSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        product_id = self.kwargs['pk']
        qs = qs.filter(product__id=product_id)
        return qs

class ProductImgmuiltiDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.ProductImages.objects.all()
    serializer_class = serializers.ProductImageSerializer

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductDetailSerializer

class RelatedProductList(generics.ListAPIView):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer
    pagination_class=pagination.PageNumberPagination

    def get_queryset(self):
        qs = super().get_queryset()
        product_id = self.kwargs['pk']
        product=models.Product.objects.get(id=product_id)
        qs = qs.filter(category=product.category).exclude(id=product_id)
        return qs

    

class CategoryList(generics.ListCreateAPIView):
    queryset = models.ProductCategory.objects.all()
    serializer_class = serializers.CategorySerializer
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        qs = super().get_queryset()
        if 'popular' in self.request.GET:
            limit = int(self.request.GET['popular'])
            qs = qs.annotate(download=Count('product')).order_by('-download', '-id')[:limit]
        return qs

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.ProductCategory.objects.all()
    serializer_class = serializers.CategoryDetailSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer

class CustomerList(generics.ListCreateAPIView):
    queryset = models.Customer.objects.all()
    serializer_class = serializers.CustomerSerializer

class CustomerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Customer.objects.all()
    serializer_class = serializers.CustomerDetailSerializer
    pagination_class = pagination.PageNumberPagination

@csrf_exempt
def Customer_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user:
            customer = models.Customer.objects.get(user=user)
            if not customer.verify_status:
                response = JsonResponse({'id': user.id, 'bool': False, 'user': user.email, 'customer_id': customer.id, 'msg': 'Account is not verified'})
            else:
                if customer.login_via_otp:
                    otp_digit = randint(100000, 999999)
                    send_mail("Your OTP", f"Your OTP digit is: {otp_digit}", "from@example.com", [customer.user.email], fail_silently=False)
                    customer.otp_digit = otp_digit
                    customer.save()
                response = JsonResponse({'id': user.id, 'bool': True, 'user': user.email, 'customer_id': customer.id, 'login_via_otp': customer.login_via_otp})
            response.set_cookie('customer_id', customer.id)
        else:
            response = JsonResponse({'bool': False, 'msg': "Invalid email/password"})
        return response
    return JsonResponse({'bool': False, 'msg': 'Invalid request method'}, status=400)

@csrf_exempt
def Customer_register(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        otp_digit = request.POST.get('otp_digit')
        hashed_password = make_password(password)

        try:
            user = User.objects.create(firstname=firstname, lastname=lastname, email=email, password=hashed_password)
            try:
                customer = models.Customer.objects.create(user=user, mobile=phone, otp_digit=otp_digit)
                send_mail("Your OTP", f"Your OTP digit is: {otp_digit}", "from@example.com", [email], fail_silently=False)
                msg = {'bool': True, 'user': user.id, 'customer': customer.id, 'msg': 'Thank you for registering, you can now log in'}
            except IntegrityError:
                user.delete()
                msg = {'bool': False, 'msg': "User mobile phone already exists"}
        except IntegrityError:
            msg = {'bool': False, 'msg': "User email already exists"}
        return JsonResponse(msg)
    return JsonResponse({'bool': False, 'msg': 'Invalid request method'}, status=400)

@csrf_exempt
def verify_custome_via_otp(request, customer_id):
    if request.method == 'POST':
        otp_digit = request.POST.get('otp_digit')
        verify = models.Customer.objects.filter(pk=customer_id, otp_digit=otp_digit).first()
        if verify:
            verify.verify_status = True
            verify.save()
            return JsonResponse({'bool': True, 'customer_id': verify.id})
        return JsonResponse({'bool': False})
    return JsonResponse({'bool': False, 'message': 'Invalid request method'}, status=400)

class OrderList(generics.ListCreateAPIView):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer

class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderDetailSerializer

class OrderItemsList(generics.ListCreateAPIView):
    queryset = models.OrderItems.objects.all()
    serializer_class = serializers.OrderItemSerializer

class OrderItemStatusModify(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.OrderItems.objects.all()
    serializer_class = serializers.OrderItemSerializer


# class OrderItemStatusModify(generics.RetrieveUpdateDestroyAPIView):
#     queryset = models.Order.objects.all()
#     serializer_class = serializers.OrderSerializer





class CustomerOrderItemsList(generics.ListAPIView):
    queryset = models.OrderItems.objects.all()
    serializer_class = serializers.OrderItemListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        customer_id = self.kwargs['pk']
        qs = qs.filter(order__customer__id=customer_id)
        return qs

class OrderItems(generics.ListCreateAPIView):
    queryset = models.OrderItems.objects.all()
    serializer_class = serializers.OrderItemSerializer


def perform_create(self, serializer):
        price = self.request.data.get('price', 0)
        serializer.save(price=price)

class OrderItemsDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.OrderItemDetailSerializer

    def get_queryset(self):
        order_id = self.kwargs['pk']
        order = models.Order.objects.get(id=order_id)
        return models.OrderItems.objects.filter(order=order)

class CustomerAddressViewset(viewsets.ModelViewSet): 
    serializer_class = serializers.CustomerAddressSerializer
    queryset = models.CustomersAddress.objects.all()

class ProductRatingViewset(viewsets.ModelViewSet): 
    serializer_class = serializers.ProductRatingSerializer
    queryset = models.ProductRating.objects.all()

@csrf_exempt
def update_order_status(request, order_id):
    if request.method == 'POST':
        update_response = models.Order.objects.filter(id=order_id).update(order_status=True)
        return JsonResponse({'bool': update_response})
    return JsonResponse({'bool': False, 'msg': 'Invalid request method'}, status=400)

class CustomerAddressList(generics.ListAPIView):
    serializer_class = serializers.CustomerAddressSerializer
    queryset = models.CustomersAddress.objects.all()  # Or any queryset you want

    def get_queryset(self):
        customer_id = self.kwargs['pk']
        return self.queryset.filter(customer__id=customer_id).order_by('id')

@csrf_exempt
def mark_default_address(request, pk):
    if request.method == 'POST':
        address_id = request.POST.get('address_id')      
        models.CustomersAddress.objects.update(default_address=False)
        res = models.CustomersAddress.objects.filter(id=address_id).update(default_address=True)
        return JsonResponse({'bool': bool(res)})
    return JsonResponse({'bool': False, 'msg': 'Invalid request method'}, status=400)

@csrf_exempt
def customer_dashboard(request, pk):
    customer_id = pk
    total_address = models.CustomersAddress.objects.filter(customer__id=customer_id).count()
    total_order = models.Order.objects.filter(customer__id=customer_id).count()
    return JsonResponse({'bool': False, 'totalAddress': total_address, 'totalOrder': total_order})

@csrf_exempt
def vendor_dashboard(request, pk):
    vendor_id = pk
    total_product = models.Product.objects.filter(vendor__id=vendor_id).count()
    total_order = models.OrderItems.objects.filter(product__vendor__id=vendor_id).count()
    total_customer =models.OrderItems.objects.filter(product__vendor__id=vendor_id).values('order__customer').distinct().count()
    order_status = True  # Or set based on your logic
      # Filter OrderItems by vendor and order status, then aggregate the total revenue
    # Filter OrderItems by vendor and order status, then aggregate the total revenue
    total_revenue = models.OrderItems.objects.filter(
        product__vendor__id=vendor_id,
        order_status=order_status
        
    ).aggregate(total_revenue=Sum(F('price') * F('qty')))
      # Extract the total revenue value
    total_revenue_value = total_revenue['total_revenue'] or 0

    return JsonResponse({'bool': False, 'totalProduct': total_product, 'totalOrder': total_order, 'totalCustomer': total_customer,'totalRevenue': total_revenue_value})

@csrf_exempt
def vendor_register(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        password = request.POST.get('password')
        otp_digit = request.POST.get('otp_digit')
        hashed_password = make_password(password)

        try:
            user = User.objects.create(firstname=firstname, lastname=lastname, email=email, password=hashed_password)
            try:
                vendor = models.Vendor.objects.create(user=user, address=address, mobile=phone, otp_digit=otp_digit)
                send_mail("Your OTP", f"Your OTP digit is: {otp_digit}", "from@example.com", [email], fail_silently=False)
                msg = {'bool': True, 'user': user.id, 'vendor': vendor.id, 'msg': 'Thank you for registering, you can now log in'}
            except IntegrityError:
                user.delete()
                msg = {'bool': False, 'msg': "User mobile phone already exists"}
        except IntegrityError:
            msg = {'bool': False, 'msg': "User email already exists"}
        return JsonResponse(msg)
    return JsonResponse({'bool': False, 'msg': 'Invalid request method'}, status=400)

@csrf_exempt
def vendor_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user:
            vendor = models.Vendor.objects.get(user=user)
            if not vendor.verify_status:
                response = JsonResponse({'id': user.id, 'bool': False, 'user': user.email, 'vendor_id': vendor.id ,'msg':"Account not verified"})
            else:
                if vendor.login_via_otp:
                    otp_digit = randint(100000,999999)
                    send_mail("Your OTP", f"Your OTP digit is: {otp_digit}", "from@example.com", [vendor.user.email], fail_silently=False)
                    vendor.otp_digit = otp_digit
                    vendor.save()
                response = JsonResponse({'id': user.id, 'bool': True, 'user': user.email, 'vendor_id': vendor.id ,'login_via_otp': vendor.login_via_otp})
        else:
            response = JsonResponse({'bool': False, 'msg': "Invalid email/password"})
        return response
    return JsonResponse({'bool': False, 'msg': 'Invalid request method'}, status=400)

@csrf_exempt
def verify_vendor_via_otp(request, vendor_id):
    if request.method == 'POST':
        otp_digit = request.POST.get('otp_digit')
        verify = models.Vendor.objects.filter(pk=vendor_id, otp_digit=otp_digit).first()
        if verify:
            verify.verify_status = True
            verify.save()
            return JsonResponse({'bool': True, 'vendor_id': verify.id})
        return JsonResponse({'bool': False})
    return JsonResponse({'bool': False, 'message': 'Invalid request method'}, status=400)



# def request_activation(request):
#     vendor = get_object_or_404(Vendor, user=request.user)
#     activation_request = VendorActivationRequest(vendor=vendor)
#     activation_request.generate_otp()
#     activation_request.send_activation_email()
#     return HttpResponse("Activation email sent.")

# def activate_vendor(request, otp_digit):
#     activation_request = get_object_or_404(VendorActivationRequest, otp_digit=otp_digit, is_active=True)
#     if activation_request.is_expired():
#         return HttpResponse("Activation link has expired.")
    
#     vendor = activation_request.vendor
#     vendor.verify_status = True
#     vendor.save()

#     activation_request.is_active = False
#     activation_request.save()

#     return HttpResponse("Vendor account activated successfully.")






@csrf_exempt
def customer_forget_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = models.User.objects.filter(email=email).first()
        if user:
            customer = models.Customer.objects.filter(user=user).first()
            if customer:
                link = f'http://localhost:3000/customer/customer-change-password/{customer.id}'
                send_mail("Password Reset Link", f"Please follow the link to reset your password: {link}", "from@example.com", [email], fail_silently=False)
                return JsonResponse({'bool': True, 'customer_id': customer.id})
            return JsonResponse({'bool': False})
        return JsonResponse({'bool': False})
    return JsonResponse({'bool': False, 'msg': 'Invalid request method'}, status=400)

@csrf_exempt
def vendor_forget_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = models.User.objects.filter(email=email).first()
        if user:
            vendor = models.Vendor.objects.filter(user=user).first()
            if vendor:
                link = f'http://mashach.pythonanywhere.com/vendor/vendor-change-password/{vendor.id}'
                send_mail("Password Reset Link", f"Please follow the link to reset your password: {link}", "from@example.com", [email], fail_silently=False)
                return JsonResponse({'bool': True, 'vendor_id': vendor.id})
            return JsonResponse({'bool': False})
        return JsonResponse({'bool': False})
    return JsonResponse({'bool': False, 'msg': 'Invalid request method'}, status=400)

@csrf_exempt
def search(request):
    if request.method == 'POST':
        data = request.POST.dict()
        if not data:
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
        query = data.get('query')
        if not query:
            return JsonResponse({'error': 'Query parameter is required'}, status=400)
        # Assuming 'query' is the search term
        products =models.Product.objects.filter(
            Q(title__icontains=query) | 
            Q(location__icontains=query) | 
            Q(category__title__icontains=query) |  # Adjust 'name' to your Category model's field
            Q(vendor__user__firstname__icontains=query))  # Adjust 'name' to your Vendor model's field
        
        product_serializer = serializers.ProductSerializer(products, many=True)
        users = models.User.objects.filter(firstname__icontains=query)
        user_serializer = serializers.UserSerializer(users, many=True)
        return JsonResponse({'products': product_serializer.data, 'users': user_serializer.data}, safe=False)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def get_order_items(request, order_id, vendor_id):
    # Fetch the vendor to ensure it exists
    vendor = get_object_or_404(models.Vendor, id=vendor_id)
    
    # Fetch the order to ensure it exists and is associated with the vendor
    order = get_object_or_404(models.Order, id=order_id)
    
    # Fetch the order items for the given order and vendor
    order_items = models.OrderItems.objects.filter(order=order, product__vendor=vendor)
    
    # Prepare the data for response
    order_items_data = [{
        'product_title': item.product.title,
        'quantity': item.qty,
        'price': item.price,
        'usd_price': item.usd_price,
    } for item in order_items]
    
    # Include additional order and customer information if needed
    response_data = {
        'order_id': str(order.id),
        'customer_name': order.customer.user.firstname,
        'customer_email': order.customer.user.email,
        'order_items': order_items_data,
    }
    
    return JsonResponse(response_data)
