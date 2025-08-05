from rest_framework import serializers
from order.models import Cart,CartItem
from product.serializers import ProductSerializer
from product.models import Product

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name','price']

class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    class Meta:
        model = CartItem
        fields = ['id','product_id','quantity']

    def save(self,**kwargs):
        cart_id =self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        
        try:
            cart_item = CartItem.objects.get(cart_id = cart_id,product_id = product_id)
            print(cart_id)
            cart_item.quantity += quantity
            self.instance = cart_item.save()
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id = cart_id, **self.validated_data)
        
        return self.instance

    def validate_product_id(self,value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError(f"product with id {value} does not exist")

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

class CartItemsSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    # product_price = serializers.SerializerMethodField(method_name="get_product_price")
    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    class Meta:
        model =CartItem
        fields = ['id','product','quantity','product','total_price']

    # def get_product_price(self,cart_item):
    #     return cart_item.product.price
    def get_total_price(self,cart_item:CartItem): #cart_item ta hocce CartItem model er ekti object eivabe define kora jay
        return cart_item.product.price * cart_item.quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemsSerializer(many = True , read_only = True)
    total_price = serializers.SerializerMethodField(method_name="get_total_price")

    class Meta:
        model = Cart
        fields = ['id','user','items','total_price']

    def get_total_price(self, cart:Cart):
        list = sum([item.product.price * item.quantity for item in cart.items.all()])
        return list