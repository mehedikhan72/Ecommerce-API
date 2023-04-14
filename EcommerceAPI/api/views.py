
from django.db import IntegrityError
from django.db.models import Q
from django.db.models.signals import post_save
from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import JsonResponse

# Create your views here.


class PostList(generics.ListCreateAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        slug = self.kwargs['slug']
        category = get_object_or_404(Category, slug=slug)
        qs = Product.objects.filter(category=category)
        return qs


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'
