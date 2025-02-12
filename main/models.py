from django.db import models

# Create your models here.
from django.conf import settings
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,UserManager
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Count,Sum
from django.utils import timezone
from datetime import timedelta
import datetime
from django.core.mail import send_mail


class CustomUserManager(UserManager):
    def _create_user(self,name,email,password,**extra_fields):
        if not email:
            raise ValueError("You have not provide a valid e-mail address")
        email=self.normalize_email(email)
        user=self.model(name,email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_user(self,name=None,email=None,password=None, **extra_fields):
        extra_fields.setdefault('is_staff',False)
        extra_fields.setdefault('is_superuser',False)
        return self._create_user(name,email,password,**extra_fields)
    
    def create_superuser(self,name=None,email=None,password=None, **extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        return self._create_user(name,email,password,**extra_fields)
    



class User(AbstractBaseUser,PermissionsMixin):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    email=models.EmailField(unique=True)
    firstname=models.CharField(max_length=255,blank=True,null=True, default='')
    lastname=models.CharField(max_length=255,blank=True,null=True, default='')

    is_active=models.BooleanField(default=True)
    is_superuser=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)

    date_joined=models.DateTimeField(default=timezone.now)
    last_login=models.DateTimeField(blank=True,null=True)

    objects=CustomUserManager()

    USERNAME_FIELD='email'
    EMAIL_FIELD='email'
    REQUIRED_FIELDS=[]





class Vendor(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user=models.ForeignKey(User,related_name='vendor_user',on_delete=models.CASCADE)
    mobile=models.PositiveBigIntegerField(unique=True,null=True)
    profile_img=models.ImageField(upload_to='vendor_img/',null=True)
    address=models.TextField(null=True)
    verify_status=models.BooleanField(default=False)
    otp_digit=models.CharField(max_length=10,null=True)
    login_via_otp=models.BooleanField(default=True)

    def __str__(self):
        return self.user.firstname

    @property
    def categories(self):
        categories = (
            Product.objects.filter(vendor=self, category__isnull=False)
            .values('category__title', 'category__id')
            .annotate(count=Count('id'))
            .order_by('category__title')
        )
        
        cat = []
        seen_titles = set()
        
        for cat in categories:
            if cat['category__title'] not in seen_titles:
                seen_titles.add(cat['category__title'])
                cat.append(cat)
        
        return cat

    # Fetch daily orders
    @property
    def show_chart_daily_orders(self):
        orders = OrderItems.objects.filter(product__vendor=self).values('order__order_time__date').annotate(count=Count('id'))
        dateList = []
        countList = []
        dataSet = {}
        if orders:
            for order in orders:
                dateList.append(order['order__order_time__date'])
                countList.append(order['count'])

        dataSet = {'dates': dateList, 'data': countList}
        return dataSet

    # Fetch weekly orders
    @property
    def show_chart_week_orders(self):
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        orders = OrderItems.objects.filter(product__vendor=self, order__order_time__date__range=[start_of_week, end_of_week]).values('order__order_time__date').annotate(count=Count('id'))
        dateList = []
        countList = []
        dataSet = {}
        for order in orders:
            dateList.append(order['order__order_time__date'])
            countList.append(order['count'])
        dataSet = {'dates': dateList, 'data': countList}
        return dataSet

    # Fetch monthly orders
    @property
    def show_chart_monthly_orders(self):
        orders = OrderItems.objects.filter(product__vendor=self).values('order__order_time__month').annotate(count=Count('id'))
        dateList = []
        countList = []
        dataSet = {}
        if orders:
            for order in orders:
                monthinteger = order['order__order_time__month']
                month = datetime.date(1900, monthinteger, 1).strftime('%B')
                dateList.append(month)
                countList.append(order['count'])
        dataSet = {'dates': dateList, 'data': countList}
        return dataSet

    # Fetch yearly orders
    @property
    def show_chart_yearly_orders(self):
        orders = OrderItems.objects.filter(product__vendor=self).values('order__order_time__year').annotate(count=Count('id'))
        dateList = []
        countList = []
        dataSet = {}
        if orders:
            for order in orders:
                dateList.append(order['order__order_time__year'])
                countList.append(order['count'])
        dataSet = {'dates': dateList, 'data': countList}
        return dataSet
# class VendorActivationRequest(models.Model):
#     vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='activation_requests')
#     otp_digit = models.CharField(max_length=10)
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_active = models.BooleanField(default=True)

#     def generate_otp(self):
#         self.otp_digit = uuid.uuid4().hex[:10]
#         self.save()
#         return self.otp_digit

#     def send_activation_email(self):
#         activation_url = f'http://yourdomain.com/activate/{self.otp_digit}/'
#         send_mail(
#             'Activate your vendor account',
#             f'Please click the following link to activate your vendor account: {activation_url}',
#             'from@example.com',
#             [self.vendor.user.email],
#             fail_silently=False,
#         )

#     def is_expired(self):
#         expiration_time = self.created_at + timedelta(hours=24)
#         return timezone.now() > expiration_time


   
#Product Category
class ProductCategory(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    title=models.CharField(max_length=200)
    detail=models.TextField(null=True)
    image=models.ImageField(upload_to='category_img/',null=True)

    def __str__(self):
        return self.title
    @property
    def total_downloads(self):
        totalDownloads=0
        products=Product.objects.filter(category=self)
        for product in products:
            if product.download:
                totalDownloads+=int(product.download)
       
        return totalDownloads     

#Product model
    

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey('ProductCategory', on_delete=models.SET_NULL, null=True)
    vendor = models.ForeignKey('Vendor', on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    detail = models.TextField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    usd_price = models.DecimalField(max_digits=10, decimal_places=2, default=80)
    tags = models.TextField(null=True)
    image = models.ImageField(upload_to='product_img/', null=True)
    product_file = models.FileField(upload_to='product_file/', null=True)
    demo_url = models.URLField(null=True, blank=True)
    location = models.CharField(max_length=200, null=True)
    download = models.CharField(max_length=200, default=0, null=True)
    publish_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    stock_quantity = models.IntegerField(default=0, null=True, blank=True)
    sku = models.CharField(max_length=100, null=True, blank=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    def isNew(self):
        is_new = self.created_at + timedelta(hours=24)
        return timezone.now() < is_new

    def __str__(self):
        return self.title

#customer model

class Customer(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user=models.ForeignKey(User,related_name='customer_user',on_delete=models.CASCADE)
    mobile=models.PositiveBigIntegerField(unique=True)
    profile_img=models.ImageField(upload_to='customer_img/',null=True)
    verify_status=models.BooleanField(default=False)
    otp_digit=models.CharField(max_length=10,null=True)
    login_via_otp=models.BooleanField(default=True)
    def __str__(self):
        return self.user.firstname


# order model

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, related_name='customer_order', on_delete=models.CASCADE, null=True)
    order_time = models.DateTimeField(auto_now_add=True)
    order_status = models.BooleanField(default=False)



 

# order item model



class OrderItems(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey('Order', related_name='order_item', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', related_name='product_item', on_delete=models.CASCADE)
    qty = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usd_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_status = models.BooleanField(default=False)

    def __str__(self):
        return self.product.title

    
# customer address model
class CustomersAddress(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    customer=models.ForeignKey(Customer,related_name='customer_address',on_delete=models.CASCADE)
    address=models.TextField()
    default_address=models.BooleanField(default=False)
   
    def __str__(self):
        return self.address

# Rating and review product

class ProductRating(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    customer=models.ForeignKey(Customer, on_delete=models.CASCADE ,related_name='rating_customers')
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='product_ratings')
    rating=models.IntegerField()
    review=models.TextField()
    add_time=models.DateTimeField(auto_now_add=True)

    def __str__(self):
       return f'Rating: {self.rating} - Review: {self.review}'


# product images model
class ProductImages(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    product=models.ForeignKey(Product,related_name='product_imgs',on_delete=models.CASCADE)
    image=models.ImageField(upload_to='product_img/',null=True)
 
    def __str__(self):
        return self.product.title

#  wishlist model
    
class WishList(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    Customer=models.ForeignKey(Customer,on_delete=models.CASCADE)

    class  Meta:
        db_table = ''
        managed = True
        verbose_name = 'Wish List'
        verbose_name_plural = 'WishList'

    def __str__(self):
        return f'{self.product.title}' -f'{self.customer.user.first_name}'  
