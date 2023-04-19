
from django.db import IntegrityError
from django.db.models import Q
from django.db.models.signals import post_save
from django.shortcuts import render, get_object_or_404
from .models import Category, Product, ProductImage, ProductSize, User
from .serializers import CategorySerializer, ProductSerializer, ImageSerializer, ProductSizeSerializer, UserRegisterSerializer, UserSerializer
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import JsonResponse
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

# Create your views here.


class ProductList(generics.ListCreateAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        slug = self.kwargs['slug']
        category = get_object_or_404(Category, slug=slug)
        qs = Product.objects.filter(category=category).order_by('-id')
        return qs


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'


class SimilarProductList(generics.ListCreateAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        slug = self.kwargs['slug']
        category = get_object_or_404(Category, slug=slug)
        qs = Product.objects.filter(category=category).order_by('-id')[:12]
        return qs


@api_view(['GET'])
@permission_classes([AllowAny])
def get_images(request, product_id):
    print(product_id)
    product = get_object_or_404(Product, id=product_id)
    images = ProductImage.objects.filter(product=product)
    serializer = ImageSerializer(images, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_available_sizes(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    sizes = ProductSize.objects.filter(
        product=product, available_quantity__gt=0)
    serializer = ProductSizeSerializer(sizes, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_size_specific_stock(request, product_id, size):
    product = get_object_or_404(Product, id=product_id)
    size = get_object_or_404(ProductSize, product=product, size=size)
    stock = size.available_quantity
    return Response(stock)

# Simple JWT


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        first_name = serializer.validated_data['first_name']
        last_name = serializer.validated_data['last_name']
        email = serializer.validated_data['email']
        phone = serializer.validated_data['phone']
        address = serializer.validated_data['address']
        password = serializer.validated_data['password']

        username = f"{first_name.lower()}.{last_name.lower()}"
        num = 1
        while User.objects.filter(username=username).exists():
            username = f"{first_name.lower()}.{last_name.lower()}.{num}"
            num += 1

        if len(password) < 8:
            return Response({'error': 'Password must be at least 8 characters'}, status=status.HTTP_400_BAD_REQUEST)
        if not email or not username or not password:
            return Response({'error': 'Please provide all fields'}, status=status.HTTP_400_BAD_REQUEST)

        User.objects.create_user(
            username=username, first_name=first_name, last_name=last_name, email=email, phone=phone, address=address, password=password)
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
    
    if serializer.errors['email'][0]:
        return Response({'error': serializer.errors['email'][0]}, status=status.HTTP_400_BAD_REQUEST)
    
    if serializer.errors['username'][0]:
        return Response({'error': serializer.errors['username'][0]}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
