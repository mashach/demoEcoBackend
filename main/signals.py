from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.db import transaction
from .models import OrderItems

notified_vendors = set()

@receiver(post_save, sender=OrderItems)
def send_order_email_to_vendor(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        order = instance.order
        vendor = product.vendor  # Assuming `vendor` is a ForeignKey in the Product model
        customer_name = order.customer.user.firstname  # Assuming `customer` is a ForeignKey in the Order model and `user` is a ForeignKey in the Customer model

        if vendor and vendor.user.email and vendor.id not in notified_vendors:  # Check if vendor and vendor email exist
            notified_vendors.add(vendor.id)  # Track the vendor to avoid duplicate emails

            # Use transaction.on_commit to ensure email is sent after the transaction is committed
            transaction.on_commit(lambda: send_order_email(vendor, customer_name, order.id))

def send_order_email(vendor, customer_name, order_id):
    subject = 'New Order Placed'
    message = f"""
Dear {vendor.user.firstname},

The product has been ordered by {customer_name}.
Order ID: {order_id}

You can view the order details at the following link:
http://localhost:3000/vendor/new-orders/{order_id}/{vendor.id}/'

Thank you,
Your Team
"""
    recipient_list = [vendor.user.email]
    send_mail(
        subject,
        message,
        'mashachb.sider@gmail.com',  # Replace with your actual 'from' email address
        recipient_list,
    )
