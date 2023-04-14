from django.urls import path
from . import views

urlpatterns = [
    # Products n category
    path('category/<slug:slug>/', views.PostList.as_view()),
    path('products/<slug:slug>/', views.PostDetail.as_view()),
]

