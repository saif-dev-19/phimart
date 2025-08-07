from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from product.models import Product,Category,Review,ProductImage
from rest_framework import status
from product.serializers import ProductSerializer,CategorySerializer,ReviewSerializer,ProductImageSerializer
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from product.filters import ProductFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter,OrderingFilter
from product.pagination import DefaultPagination
from api.permission import IsAdminOrReadOnly,FullDjangoModelPermission
from rest_framework.permissions import DjangoModelPermissions
from product.permissions import IsReviewAurthorOrReadOnly
from drf_yasg.utils import swagger_auto_schema



# Create your views here.

class ProductViewSet(ModelViewSet):
     """
     API endpoint for managing products in the e-commerce store
     - Allow authenticated admin to create,update,and delete products
     - Allows user to browse and filter product
     - Support searching by name, description, and category
     - Support ordering by price and updated-at
     """
     queryset = Product.objects.all()
     serializer_class = ProductSerializer
     filter_backends= [DjangoFilterBackend,SearchFilter,OrderingFilter]
     pagination_class = DefaultPagination
     filterset_class =  ProductFilter
     search_fields = ['name','category__name'] #note in notion, check notion phi-mart implementing
     ordering_fields = ['price','created_at']
     permission_classes = [IsAdminOrReadOnly]
     # permission_classes = [DjangoModelPermissions]
     # permission_classes = [FullDjangoModelPermission]
     # permission_classes = [IsAdminUser]
     # permission_classes = [IsAdminOrReadOnly]
     # permission_classes = [DjangoModelPermissionsOrAnonReadOnly]

     # def get_permissions(self):
     #      if self.request.method == "GET":
     #           return [AllowAny()]
     #      return [IsAdminUser()]

     # def get_queryset(self):
     #      queryset = Product.objects.all()
     #      category_id = self.request.query_params.get('category_id')

     #      if category_id is not None:
     #           queryset = Product.objects.filter(category_id = category_id)
     #      return queryset
     
     # def destroy(self, request, *args, **kwargs):
     #      product = self.get_object()
     #      if product.stock > 10:
     #           return Response({"message":"Product with stock more then 10 could not be deleted"})
     #      self.perform_destroy(product)
     #      return Response(status= status.HTTP_204_NO_CONTENT)

     @swagger_auto_schema(
               operation_summary= "Retrive a list of product"
     )
     def list(self, request, *args, **kwargs):
          """Retrive all the products"""
          return super().list(request, *args, **kwargs)
     
     @swagger_auto_schema(
               operation_summary= "Create a product by admin",
               operation_description= "This allow an admin to create a project",
               responses={
                    201:ProductSerializer,
                    400 : "Bed Request"
               }
     )
     def create(self, request, *args, **kwargs):
          """Only Authenticated Admin can create product"""
          return super().create(request, *args, **kwargs)
     


class ProductImageViews(viewsets.ModelViewSet):
     serializer_class = ProductImageSerializer
     permission_classes = [IsAdminOrReadOnly]
     def get_queryset(self):
          return ProductImage.objects.filter(product_id = self.kwargs.get('product_pk'))
     
     def perform_create(self, serializer):
          serializer.save(product_id = self.kwargs.get('product_pk'))


class CategoryViewSet(viewsets.ModelViewSet):
     queryset = Category.objects.annotate(product_count = Count('products')).all()
     serializer_class = CategorySerializer
     permission_classes = [IsAdminOrReadOnly]



class ReviewViewSet(viewsets.ModelViewSet):
     serializer_class = ReviewSerializer
     permission_classes = [IsReviewAurthorOrReadOnly]

     def perform_create(self, serializer): # eta hocce reivew er get method e ba review te user id thik vabe dekhanor jonno.
          serializer.save(user = self.request.user) #eta r serailizer er product id er jonno def create 2 tai same kaj kore, easy way eta. context patano
     
     def get_queryset(self):
          return Review.objects.filter(product_id = self.kwargs.get('product_pk'))
     
     def get_serializer_context(self):
          return {'product_id':self.kwargs.get('product_pk')}
     






'''Product View set replace

@api_view(['GET','PUT','DELETE'])
def view_specific_products(request,id): 
        if request.method == "GET":
            product = get_object_or_404(Product,pk=id)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        if request.method == 'PUT':
             product = get_object_or_404(Product,pk=id)
             serializer =ProductSerializer(product, data = request.data)
             serializer.is_valid(raise_exception= True)
             serializer.save()
             return Response(serializer.data)
        if request.method == 'DELETE':
             product = get_object_or_404(Product,pk=id)
             copy_of_delete_product = product
             product.delete()
             serializer = ProductSerializer(copy_of_delete_product)
             return Response(serializer.data,status= status.HTTP_204_NO_CONTENT)

class ViewSpecificProduct(APIView):
     def get(self,request,id):
            product = get_object_or_404(Product,pk=id)
            serializer = ProductSerializer(product)
            return Response(serializer.data)  
     def put(self,request,id):
            product = get_object_or_404(Product,pk=id)
            serializer =ProductSerializer(product, data = request.data)
            serializer.is_valid(raise_exception= True)
            serializer.save()
            return Response(serializer.data) 
     def delete(self,request,id):
            product = get_object_or_404(Product,pk=id)
            copy_of_delete_product = product
            product.delete()
            serializer = ProductSerializer(copy_of_delete_product)
            return Response(serializer.data,status= status.HTTP_204_NO_CONTENT)
--------------------
class ProductDetails(RetrieveUpdateDestroyAPIView):
     queryset = Product.objects.all()
     serializer_class = ProductSerializer
     lookup_field = "id"

     def delete(self, request, *args, **kwargs):
          product = get_object_or_404(Product,pk = id)
          if product.stock > 10:
               return Response({"message":"Product with stock more then 10 could not be deleted"})
          product.delete()
          return Response(status= status.HTTP_204_NO_CONTENT)


@api_view(['GET','POST'])
def view_products(request):
    if request.method == 'GET':
        products = Product.objects.select_related('category').all()
        serializer = ProductSerializer(products,many = True)
        return Response(serializer.data) 
      
    if request.method == 'POST':
        serializer = ProductSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ViewProduct(APIView):
     def get(self,request):
        products = Product.objects.select_related('category').all()
        serializer = ProductSerializer(products,many = True)
        return Response(serializer.data)
     def post(self,request):
        serializer = ProductSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED) 

class ViewProductList(ListCreateAPIView):
     queryset = Product.objects.select_related('category').all()
     serializer_class = ProductSerializer
     def get_queryset(self):
          return Product.objects.select_related('category').all()
     
     def get_serializer_class(self):
          return ProductSerializer


'''



'''Category View Set Replace

@api_view()   
def view_categories(request):
    categories = Category.objects.annotate(product_count = Count('products')).all()
    serializer = CategorySerializer(categories,many = True)
    return Response(serializer.data)

class ViewCategories(APIView):
     def get(self,request):
        categories = Category.objects.annotate(product_count = Count('products')).all()
        serializer = CategorySerializer(categories,many = True)
        return Response(serializer.data)
     def post(self,request):
          serializer = CategorySerializer(data = request.data)
          serializer.is_valid(raise_exception=True)
          serializer.save()
          return Response(serializer.data,status=status.HTTP_201_CREATED)


class ViewCategoryList(ListCreateAPIView):
     queryset = Category.objects.annotate(product_count = Count('products')).all()
     serializer_class = CategorySerializer



@api_view()
def view_specific_category(request,pk):
      category = get_object_or_404(Category,pk=pk)
      serializer = CategorySerializer(category)
      return Response(serializer.data)


class ViewSpecificCategory(APIView):
     def get(self,request,pk):
        category = get_object_or_404(Category.objects.annotate(product_count = Count('products')).all(),pk=pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)
     def put(self,request,pk):
          categroy = get_object_or_404(Category.objects.annotate(product_count = Count('products')).all(),pk=pk)
          serializer = CategorySerializer(categroy, data = request.data)
          serializer.is_valid(raise_exception=True)
          serializer.save()
          return Response(serializer.data)
     def delete(self,request,pk):
          category = get_object_or_404(Category.objects.annotate(product_count = Count('products')).all(),pk=pk)
          category.delete()
          return Response(status= status.HTTP_204_NO_CONTENT)


class CategoryDetails(RetrieveUpdateDestroyAPIView):
     queryset = Category.objects.annotate(product_count = Count('products')).all()
     serializer_class = CategorySerializer


'''