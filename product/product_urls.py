from product import views
from django.urls import path,include


urlpatterns = [
    path("<int:id>/",views.ProductDetails.as_view(),name="product-list"),
    path("",views.ViewProductList.as_view(),name="product-list"),
    
]


