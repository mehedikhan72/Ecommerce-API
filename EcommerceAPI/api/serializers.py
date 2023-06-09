from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductSize, User, Order, OrderItem, WishList, QnA, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'regular_price',
                  'discount_price', 'stock', 'slug', 'intro_image', 'total_ratings',
                  'total_reviews', 'avg_rating', 'category']


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
                  'email', 'phone', 'address', 'date_ordered', 'status', 'shipping_charge',
                  'outside_comilla', 'payment_method', 'total', 'transaction_id', 'online_paid']


class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer()
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'size', 'price']


class WishListSerializer(serializers.ModelSerializer):
    user = UserDataSerializer1()
    product = ProductSerializer()

    class Meta:
        model = WishList
        fields = ['id', 'user', 'product', 'date']


class QnASerializer(serializers.ModelSerializer):
    user = UserDataSerializer1()
    answer = serializers.CharField(max_length=1000, required=False)
    product = ProductSerializer(required=False)

    class Meta:
        model = QnA
        fields = ['id', 'question', 'answer', 'date', 'product', 'user']


class ReviewSerializer(serializers.ModelSerializer):
    user = UserDataSerializer1(required=False)
    product = ProductSerializer(required=False)

    class Meta:
        model = Review
        fields = ['id', 'review', 'rating', 'date', 'product', 'user']