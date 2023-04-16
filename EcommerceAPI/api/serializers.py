from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductSize


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'regular_price', 'discount_price', 'stock', 'slug', 'intro_image', 'category']

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image']

class ProductSizeSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = ProductSize
        fields = ['id', 'product', 'size', 'available_quantity'] 