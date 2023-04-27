from django.urls import path
from . import views
from .views import MyTokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    # Products n category
    path('category/<slug:slug>/', views.ProductList.as_view()),
    path('product/<slug:slug>/', views.ProductDetail.as_view()),
    path('similar_products/<slug:slug>/', views.SimilarProductList.as_view()),
    path('get_available_sizes/<int:product_id>/',
         views.get_available_sizes, name='get_available_sizes'),
    path('get_size_specific_stock/<int:product_id>/<str:size>/',
         views.get_size_specific_stock, name='get_size_specific_stock'),
    path('get_categories/', views.CategoryList.as_view(), name='get_categories'),

    # images
    path('images/<int:product_id>/', views.get_images, name='get_images'),
    path('upload_images/<int:product_id>/', views.upload_images, name='upload_images'),

    # Simple jwt
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Register user
    path('register/user/', views.register_user, name='register'),

    # Orders
    path('place_order/', views.place_order, name='place_order'),

    # Utils
    path('get_user_data/<int:user_id>/', views.get_user_data, name='get_user_data'),
    path('add_product_sizes/<int:product_id>/', views.add_product_sizes, name='add_product_sizes'),

    # Search
    path('search/', views.SearchList.as_view(), name='get_search_data'),
]
