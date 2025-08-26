from django.shortcuts import render
from order.serializer import EmptySerializer,CartSerializer,CartItemsSerializer,AddCartItemSerializer,UpdateCartItemSerializer,OrderSerializer,CreateOrderSerializer,OrderUpdateSerializer
from order.serializer import OrderUpdateSerializer 
from rest_framework.viewsets import GenericViewSet,ModelViewSet
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin
from order.models import Cart,CartItem,Order,OrderItem
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.decorators import action
from order.services import OrderServices
from rest_framework.response import Response
# Create your views here.


class CartViewSet(CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

    def get_queryset(self):
        if getattr(self,'swagger_fake_view',False):
            return Cart.objects.none()
        return Cart.objects.prefetch_related('items__product').filter(user = self.request.user) #jar cart sudu sei dekhte parbe tai use korce ei def


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get','post','patch','delete']
    
    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemsSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        if getattr(self, 'swagger_fake_view', False):
            return context
        
        return {'cart_id': self.kwargs.get('cart_pk')}

    def get_queryset(self):
        return CartItem.objects.select_related('product').filter(cart_id = self.kwargs.get('cart_pk'))


class OrderViewSet(ModelViewSet):
    
    http_method_names = ['get','post','delete','patch','head','options']

    @action(detail=True, methods=['post'], permission_classes =[IsAuthenticated])
    def cancel(self,request,pk=None): #cancel action er maddome order cancel kora jabe post method e
        order = self.get_object()
        OrderServices.cancel_order(order = order, user = request.user)
        return Response({'status':'Order Canceled'})
    
    @action(detail=True, methods=['patch'], permission_classes =[IsAdminUser]) #permission er jonno jodi method override kori jemn niche, tahole ei mothod gulor vitore permission_classes kaj kore na. var hisebe thakle korbe kaj
    def update_status(self,request,pk=None):
        order = self.get_object()
        serializer = OrderUpdateSerializer(order,data=request.data, partial = True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status':f'Order Status updated to {request.data['status']}'})
        

    def get_permissions(self):
        if self.action in ['update_status','destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'cancel':
            return EmptySerializer
        if self.request.method == 'POST':
            return CreateOrderSerializer
        if self.request.method == 'PATCH':
            return OrderUpdateSerializer
        return OrderSerializer

    def get_serializer_context(self):
        if getattr(self,'swagger_fake_view',False):
            return super().get_serializer_context()
        return {'user_id' : self.request.user.id, 'user' : self.request.user}

    def get_queryset(self):
        if getattr(self,'swagger_fake_view',False):
            return Order.objects.none
        if self.request.user.is_staff:
            return Order.objects.prefetch_related('items__product').all() # prefatch_related karon order er modde product nai, product ache orderItem er modde tai order theke items then product ke access
        return Order.objects.prefetch_related('items__product').filter(user = self.request.user)
    