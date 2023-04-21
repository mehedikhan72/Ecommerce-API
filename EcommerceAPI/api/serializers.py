from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductSize, User, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'regular_price',
                  'discount_price', 'stock', 'slug', 'intro_image', 'category']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image']


class ProductSizeSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = ProductSize
        fields = ['id', 'product', 'size', 'available_quantity']


class UserDataSerializer1(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name',
                  'email', 'phone', 'address']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name',
                  'email', 'phone', 'address', 'password']

        def create(self, validated_data):
            password = validated_data.pop('password')
            user = User(**validated_data)
            user.set_password(password)
            user.save()

            return user


class OrderSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=False)
    username = serializers.CharField(max_length=100, required=False)
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(max_length=100, required=False)
    phone = serializers.CharField(max_length=100, required=False)
    address = serializers.CharField(max_length=300, required=False)

    class Meta:
        model = Order
        fields = ['id', 'user_id', 'username', 'first_name', 'last_name',
                  'email', 'phone', 'address', 'date_ordered', 'delivered', 'shipping_charge']


class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer()
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'size', 'price']
