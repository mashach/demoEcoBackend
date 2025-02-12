from rest_framework  import  serializers
from .import models
from django.contrib.auth.models import User
from django.core.mail import send_mail


class VendorDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Vendor
        fields=['id','user','mobile','address','profile_img','show_chart_daily_orders','show_chart_week_orders','show_chart_monthly_orders','show_chart_yearly_orders','categories','login_via_otp']
    def __init__(self,*args,**kwargs):
        super(VendorDetailSerializer,self).__init__(*args,**kwargs)
        # self.Meta.depth=1


    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = UserSerializer(instance.user).data
        # response['customer_order'] = OrderSerializer(instance.customer_order).data
        return response

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.ProductImages
        fields=['id','product','image']

class ProductSerializer(serializers.ModelSerializer):
    product_imgs=ProductImageSerializer(many=True,read_only=True)
    
    product_rating=serializers.StringRelatedField(many=True,read_only=True)
    class Meta:
        model=models.Product
        fields=['id','category','vendor','title','detail','price','product_rating','product_imgs','usd_price','image','demo_url','tags','product_file','download','publish_status','created_at','location','isNew']
    def __init__(self,*args,**kwargs):
        super(ProductSerializer,self).__init__(*args,**kwargs)
        # self.Meta.depth=1


        


#product detail serializer
class ProductDetailSerializer(serializers.ModelSerializer):
    product_ratings=serializers.StringRelatedField(many=True,read_only=True)
    product_imgs=ProductImageSerializer(many=True,read_only=True)
    
    class Meta:
        model=models.Product
        fields=['id','category','vendor','title','detail','price','product_ratings','product_imgs','usd_price','image','demo_url','tags','product_file','download','publish_status','location','isNew']
    def __init__(self,*args,**kwargs):
        super(ProductDetailSerializer,self).__init__(*args,**kwargs)
        # self.Meta.depth=1


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=models.ProductCategory
        fields=['id','title','detail','image','total_downloads']
    def __init__(self,*args,**kwargs):
        super(CategorySerializer,self).__init__(*args,**kwargs)
        
        # self.Meta.depth=1

class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Vendor
        fields=['id','title','detail','image']
    def __init__(self,*args,**kwargs):
        super(CategoryDetailSerializer,self).__init__(*args,**kwargs)
        # self.Meta.depth=1

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.User
        fields=['id','firstname','lastname','email']




    
class CustomerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Customer
        fields = ['id', 'user', 'mobile', 'otp_digit','login_via_otp']  # Include 'user' field


      

class CustomerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Customer
        fields=['id','user','mobile','profile_img','customer_order','otp_digit','login_via_otp']
    # def __init__(self,*args,**kwargs):
    #     super(CustomerDetailSerializer,self).__init__(*args,**kwargs)
    #     # self.Meta.depth=1
  
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = UserSerializer(instance.user).data
        # response['customer_order'] = OrderSerializer(instance.customer_order).data
        return response
    def create(self, validated_data):
        user = validated_data['user']
        email = user
        otp_digit = validated_data['otp_digit']
        instance = super(CustomerDetailSerializer, self).create(validated_data)
        
        # Send email
        send_mail(
            "Verify Account",
            "Please verify your account.",
            "mashachb.sider@gmail.com",
            [email],
            fail_silently=False,
            html_message=f'Your OTP is <p>{otp_digit}</p>'
        )
        print(email)
        return instance


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=models.Customer.objects.all())  # Ensure customer is required
    
    class Meta:
        model =models.Order
        fields = ['id', 'customer', 'order_time', 'order_status']



class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.OrderItems
        fields=['id','order','product',]
    def __init__(self,*args,**kwargs):
        super(OrderDetailSerializer,self).__init__(*args,**kwargs)
        self.Meta.depth=1


class OrderItemListSerializer(serializers.ModelSerializer):
    # order = OrderSerializer()
    # product = ProductSerializer()

    class Meta:
        model = models.OrderItems
        fields = ['id', 'order', 'product', 'qty', 'price','order_status']

    def to_representation(self, instance):
        response = super().to_representation(instance)  # Initialize response here

        # Now you can access and modify response
        response['order'] = OrderSerializer(instance.order).data
        response['user'] = UserSerializer(instance.order.customer.user).data
        response['customer'] = CustomerSerializer(instance.order.customer).data
        response['product'] = ProductDetailSerializer(instance.product).data

        return response


        
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.OrderItems
        fields=['id','order','product', 'qty', 'price','usd_price','order_status']







class OrderItemDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.OrderItems
        fields=['id','order','product', 'qty', 'price']
    def __init__(self,*args,**kwargs):
        super(OrderItemDetailSerializer,self).__init__(*args,**kwargs)
        # self.Meta.depth=1


class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.CustomersAddress
        fields=['id','customer','address','default_address']
    def __init__(self,*args,**kwargs):
        super(CustomerAddressSerializer,self).__init__(*args,**kwargs)
        # self.Meta.depth=1


class ProductRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.ProductRating
        fields=['id','customer','product','rating','review','add_time']
    def __init__(self,*args,**kwargs):
        super(ProductRatingSerializer,self).__init__(*args,**kwargs)
        # self.Meta.depth=1



    
class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Vendor
        fields=['id','user','address','mobile','profile_img','categories','login_via_otp']
    def __init__(self,*args,**kwargs):
        super(VendorSerializer,self).__init__(*args,**kwargs)
        #self.Meta.depth=1

      
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = UserSerializer(instance.user).data
        # response['customer_order'] = OrderSerializer(instance.customer_order).data
        return response

