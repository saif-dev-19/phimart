from product import views
from django.urls import path


urlpatterns = [
    path("",views.ViewCategoryList.as_view(),name="category-list"),
    path("<int:pk>/",views.CategoryDetails.as_view(),name="view-specific-category"),
]


