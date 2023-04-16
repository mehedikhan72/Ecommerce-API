from django.urls import path
from . import views

urlpatterns = [
    # Products n category
    path('category/<slug:slug>/', views.ProductList.as_view()),
    path('product/<slug:slug>/', views.ProductDetail.as_view()),
    path('similar_products/<slug:slug>/', views.SimilarProductList.as_view()),

    # images
    path('images/<int:product_id>/', views.get_images, name='get_images'),
]
