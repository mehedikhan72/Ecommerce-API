from django.urls import path
from . import views
from .views import MyTokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    # Products n category3Aa
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
    path('upload_images/<int:product_id>/',
         views.upload_images, name='upload_images'),

    # Simple jwt
    path('token/', MyTokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),

    # Register user
    path('register/user/', views.register_user, name='register'),

    # Orders
    path('place_order/', views.place_order, name='place_order'),
    path('orders/', views.OrderList.as_view(), name='orders'),
    path('get_order_items/<int:order_id>/', views.get_order_items, name='get_order_items'),
    path('change_order_status/<int:id>/', views.change_order_status, name='change_order_status'),

    # Utils
    path('get_user_data/<int:user_id>/',
         views.get_user_data, name='get_user_data'),
    path('add_product_sizes/<int:product_id>/',
         views.add_product_sizes, name='add_product_sizes'),

    # Search
    path('search/', views.SearchList.as_view()),

    # Wishlist
    path('wishlist/', views.get_wishlist_items, name='get_wishlist_items'),
    path('change_wishlist/<slug:slug>/',
         views.change_wishlist, name='change_wishlist'),
    path('if_in_wishlist/<slug:slug>/',
         views.if_in_wishlist, name='if_in_wishlist'),

    # QnA
    path('qna/<slug:slug>/', views.QnAList.as_view()),
    path('add_question/<slug:slug>/', views.add_question, name='add_question'),
    path('add_answer/<int:qna_id>/', views.add_answer, name='add_answer'),
    path('unanswered_questions/', views.UnansweredList.as_view(),
         name='unanswered_questions')
]
