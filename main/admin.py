from django.contrib import admin
from .models import User,Vendor,Product,ProductCategory,Customer,Order,OrderItems,CustomersAddress,ProductRating,ProductImages

admin.site.register(User)
admin.site.register(Vendor)
admin.site.register(ProductCategory)

class CustomerAdmin(admin.ModelAdmin):
    list_display=['get_username','mobile']
    def get_username(self,obj):
        return obj.user.email
    
class ProductAdmin(admin.ModelAdmin):
    list_display=['title','price','usd_price']
    list_editable=['usd_price']

class OrderAdmin(admin.ModelAdmin):
    list_display=['id','customer','order_time','order_status']
    
    
    
admin.site.register(Order,OrderAdmin)    
admin.site.register(Product,ProductAdmin)
admin.site.register(Customer,CustomerAdmin)
admin.site.register(OrderItems)
admin.site.register(CustomersAddress)
admin.site.register(ProductRating)
admin.site.register(ProductImages)

# Register your models here.
