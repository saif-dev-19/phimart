from order.models import Order,OrderItem,Cart
from django.db import transaction
from rest_framework.exceptions import PermissionDenied,ValidationError

class OrderServices:
    @staticmethod
    def CreateOrder(user_id,cart_id):
        with transaction.atomic():
            cart = Cart.objects.get(pk = cart_id)
            cart_items = cart.items.select_related('product').all()
            total_price = sum([item.product.price * item.quantity for item in cart_items])

            order = Order.objects.create(user_id = user_id,total_price = total_price)
        

            order_items = [
                OrderItem(
                    order = order,
                    product = item.product,
                    quantity = item.quantity,
                    price = item.product.price,
                    total_price = item.product.price * item.quantity
                )
                for item in cart_items
            ]
            # [<object(1)>, <object(2)>]

            OrderItem.objects.bulk_create(order_items) #eksathe ekadik object create korte bulk_create use hoy. 

            cart.delete()

            return order
        
    @staticmethod
    def cancel_order(order,user):
        if user.is_staff:
            order.status = Order.CANCELED
            order.save()
            return order
        
        if order.user != user:
            raise PermissionDenied({'detail':"You can only cancel your now order"})
        
        if order.status == Order.DELIVERED:
            raise ValidationError({'deatil':"You can not cancel an order"})
        
        order.status = Order.CANCELED
        order.save()
        return order
