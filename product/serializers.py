from rest_framework import serializers
from decimal import Decimal
from product.models import Category,Product,Review,ProductImage
from django.contrib.auth import get_user_model


# class CategorySerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     name = serializers.CharField()
#     description = serializers.CharField()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name','description','product_count']
    
    product_count = serializers.IntegerField(read_only = True, help_text = "Return the number product in this category")

# class ProductSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     name = serializers.CharField()
#     unit_price = serializers.DecimalField(max_digits=10,decimal_places=2, source = 'price')

#     price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
#     # category = serializers.PrimaryKeyRelatedField(queryset =Category.objects.all())
#     # category = serializers.StringRelatedField()
#     # category = CategorySerializer() #category er vitorer sob kicu access korar jonno
#     category = serializers.HyperlinkedRelatedField(
#         queryset = Category.objects.all(),
#         view_name = 'view-specific-category',
#     )

#     def calculate_tax(self,product):
#         return round(product.price * Decimal(1.1))



class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    class Meta:
        model = ProductImage
        fields = ['id','image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many = True, read_only = True)
    class Meta:
        model = Product
        fields = ['id','name','images','description','price','stock','category','price_with_tax']


    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    def calculate_tax(self,product):
        return round(product.price * Decimal(1.1))
    
    def validate_price(self,price):
        if price < 0:
            raise serializers.ValidationError("price could not be negative")
        else:
            return price


class SimpleUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(
        method_name="get_current_user_name")
    class Meta:
        model = get_user_model()
        fields = ['id','name']


    def get_current_user_name(self,obj):
        return obj.get_full_name()






class ReviewSerializer(serializers.ModelSerializer):
    # user = serializers.CharField(read_only = True)
    # user = SimpleUserSerializer()
    user = serializers.SerializerMethodField(method_name='get_user')#nested serializer line 76
    class Meta:
        model = Review
        fields = ['id','user','product','ratings','comment']
        read_only_fields = ['user','product'] #upoer user er moto koreo read only kora jabe  caile

    def get_user(self,obj):
        return SimpleUserSerializer(obj.user).data #nested serializer line 70

    def create(self, validated_data):
        product_id = self.context['product_id']
        review = Review.objects.create(product_id = product_id, **validated_data)
        return review