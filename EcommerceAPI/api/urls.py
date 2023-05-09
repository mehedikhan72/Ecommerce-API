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
    path('get_order_items/<int:order_id>/',
         views.get_order_items, name='get_order_items'),
    path('change_order_status/<int:id>/',
         views.change_order_status, name='change_order_status'),

    # Utils
    path('get_user_data/<int:user_id>/',
         views.get_user_data, name='get_user_data'),
    path('add_product_sizes/<int:product_id>/',
         views.add_product_sizes, name='add_product_sizes'),
    path('edit_account/<int:id>', views.edit_account, name='edit_account'),

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
         name='unanswered_questions'),

    # New arrivals
    path('new_arrivals/', views.new_arrivals, name='new_arrivals'),

    # Tracking orders
    path('get_user_orders/', views.get_user_orders, name='get_user_orders'),

    # managing moderators
    path('get_moderators/', views.get_moderators, name='get_moderators'),
    path('change_moderator_status/<int:user_id>/',
         views.change_moderator_status, name='change_moderator_status'),
    path('get_users/<str:query>/', views.get_users, name='get_users'),
    path('change_pass_test/', views.change_pass_test, name='change_pass_test'),

    # Reviews
    path('get_reviews/<slug:slug>/',
         views.ReviewList.as_view(), name='get_reviews'),
    path('create_review/<slug:slug>/', views.create_review, name='create_review'),
    path('is_eligible_reviewer/<slug:slug>/',
         views.is_eligible_reviewer, name='is_eligible_reviewer'),

    # Payment
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/fail/', views.payment_fail, name='payment_fail'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),

    # Edit product
     path('edit_product/<slug:slug>/', views.edit_product, name='edit_product'),
]
