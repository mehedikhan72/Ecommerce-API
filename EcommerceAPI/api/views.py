import os
from django.shortcuts import redirect
import requests
from django.http import HttpResponseBadRequest
import uuid
from sslcommerz_lib import SSLCOMMERZ
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Q
from django.db.models.signals import post_save
from django.shortcuts import render, get_object_or_404
from .models import Category, Product, ProductImage, ProductSize, User, Order, OrderItem, WishList, QnA
from .serializers import CategorySerializer, ProductSerializer, ImageSerializer, ProductSizeSerializer, UserRegisterSerializer, OrderSerializer, OrderItemSerializer, UserDataSerializer1, WishListSerializer, QnASerializer
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import JsonResponse
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import PermissionDenied

# Create your views here.


class ProductList(generics.ListCreateAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        slug = self.kwargs['slug']
        category = get_object_or_404(Category, slug=slug)
        qs = Product.objects.filter(category=category).order_by('-id')
        return qs

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            if self.request.user.is_moderator or self.request.user.is_admin:
                slug = self.kwargs['slug']
                category = get_object_or_404(Category, slug=slug)
                serializer.save(category=category)
                return Response(serializer.data)
            else:
                raise PermissionDenied(
                    "You are not authorized to take this action!")
        else:
            raise PermissionDenied(
                "Credentials were not provided!")


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


class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def get_images(request, product_id):
    print(product_id)
    product = get_object_or_404(Product, id=product_id)
    images = ProductImage.objects.filter(product=product)
    serializer = ImageSerializer(images, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_images(request, product_id):
    user = request.user
    if user.is_moderator or user.is_admin:
        product = get_object_or_404(Product, id=product_id)
        images = request.FILES.getlist('images')
        print(images)

        if not images:
            return JsonResponse({
                'error': 'No images were provided!'
            })

        if (len(images) >= 10):
            return JsonResponse({
                "Error": "More than 10 images is not allowed."
            })

        for image in images:
            product_image = ProductImage.objects.create(
                product=product, image=image)
            product_image.save()

        product.intro_image = images[0]
        product.save()

        return JsonResponse({
            'success': 'Images were uploaded successfully!'
        })

    else:
        raise PermissionDenied(
            "You are not authorized to take this action!")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_product_sizes(request, product_id):
    user = request.user
    if user.is_moderator or user.is_admin:
        product = get_object_or_404(Product, id=product_id)
        sizes = request.data

        if not sizes:
            return JsonResponse({
                'error': 'No sizes were provided!'
            })

        for s in sizes:
            size = s['size']
            available_quantity = s['available_quantity']
            product_size = ProductSize.objects.create(
                product=product, size=size, available_quantity=available_quantity
            )
            product_size.save()

        return JsonResponse({
            'success': 'Sizes were added successfully!'
        })

    else:
        raise PermissionDenied(
            "You are not authorized to take this action!")


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
        token['is_moderator'] = user.is_moderator
        token['is_admin'] = user.is_admin

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


# Payment Logic Begins

# TODO: use env variables for all of the sensitive data
# TODO: might store some other payment related info in the db.
# TODO: Add more security layers to this..(the ones chatGPT mentioned.)

@api_view(['POST'])
def payment_success(request):
    transaction_id = request.POST.get('tran_id')
    try:
        order = Order.objects.get(transaction_id=transaction_id)
    except Order.DoesNotExist:
        return HttpResponseBadRequest("Invalid transaction ID")

    val_id = request.POST.get('val_id')
    store_id = os.environ.get('STORE_ID')
    store_passwd = os.environ.get('STORE_PASSWD')
    print(store_id)

    # Construct the validation API URL
    url = f"https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php?val_id={val_id}&store_id={store_id}&store_passwd={store_passwd}&format=json"

    response = requests.get(url, verify=True)
    response_json = response.json()

    if response_json['status'] == 'VALID':
        order.online_paid = True
        order.save()
        return redirect(f'http://localhost:3000/payment-result?status=success')
    else:
        order.delete()
        return redirect(f'http://localhost:3000/payment-result?status=fail')


@api_view(['POST'])
def payment_fail(request):
    transaction_id = request.POST.get('tran_id')
    order = Order.objects.get(transaction_id=transaction_id)
    order.delete()

    return redirect(f'http://localhost:3000/payment-result?status=fail')


@api_view(['POST'])
def payment_cancel(request):
    transaction_id = request.POST.get('tran_id')
    order = Order.objects.get(transaction_id=transaction_id)
    order.delete()

    return redirect(f'http://localhost:3000/payment-result?status=cancel')


def get_total(order_data):
    order_items_array = order_data['order_items']
    total = 0

    for item in order_items_array:
        if item['productData']['discount_price']:
            total += item['productData']['discount_price'] * item['quantity']
        else:
            total += item['productData']['regular_price'] * item['quantity']

    total += order_data['shipping_charge']
    return total


def request_ssl_session(order_data, transaction_id):
    total = get_total(order_data)
    settings = {
        'store_id': os.environ.get('STORE_ID'),
        'store_pass': os.environ.get('STORE_PASSWD'),
        'issandbox': True
    }

    sslcz = SSLCOMMERZ(settings)
    post_body = {}
    post_body['total_amount'] = total
    post_body['currency'] = "BDT"
    post_body['tran_id'] = transaction_id
    post_body['success_url'] = "http://127.0.0.1:8000/api/payment/success/"
    post_body['fail_url'] = "http://127.0.0.1:8000/api/payment/fail/"
    post_body['cancel_url'] = "http://127.0.0.1:8000/api/payment/cancel/"
    post_body['emi_option'] = 0
    post_body['cus_name'] = order_data['order']['first_name']
    post_body['cus_email'] = order_data['order']['email']
    post_body['cus_phone'] = order_data['order']['phone']
    post_body['cus_add1'] = order_data['order']['address']
    post_body['cus_city'] = "Dhaka"
    post_body['cus_country'] = "Bangladesh"
    post_body['shipping_method'] = "NO"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = 1
    post_body['product_name'] = "Test"
    post_body['product_category'] = "Test Category"
    post_body['product_profile'] = "general"

    return sslcz.createSession(post_body)  # API response

# Payment Logic Ends

# TODO: reduce size quantities based on new orders.
# TODO: Fix shipping charge logic. 


@api_view(['POST'])
@permission_classes([AllowAny])
def place_order(request):
    # I will have to create an Order first and then the order items.
    # I will have to check if the user is authenticated or not.

    serializer = OrderSerializer(data=request.data['order'])
    order = None
    if serializer.is_valid():
        order = serializer.save()
        order.shipping_charge = request.data['shipping_charge']
        order.payment_method = request.data['payment_method']
        total = get_total(request.data)
        order.total = total
        if request.data['shipping_charge'] == 50:
            order.outside_comilla = False
        else:
            order.outside_comilla = True

        # if payment is online, begin payment logic. else bypass the order for Cash on delivery.
        if request.data['payment_method'] == 'online':
            transaction_id = uuid.uuid4().hex
            order.transaction_id = transaction_id
            order.online_paid = False
            order.save()

            ssl_response = request_ssl_session(request.data, transaction_id)
            if not ssl_response['status'] == 'SUCCESS':
                return Response({'error': 'Payment gateway error.'}, status=status.HTTP_400_BAD_REQUEST)
        elif request.data['payment_method'] == 'COD':
            order.save()
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    order_items_array = request.data['order_items']

    for item in order_items_array:
        order = get_object_or_404(Order, id=order.id)
        product = get_object_or_404(Product, id=item['productData']['id'])
        quantity = item['quantity']
        size = item['size'][0]['size']
        print(size)

        # Get product price from the backend since the user can change the price in the frontend.
        price = 0
        if product.discount_price:
            price = product.discount_price * quantity
        else:
            price = product.regular_price * quantity

        if order and product and quantity and size and price:
            try:
                order_item = OrderItem.objects.create(
                    order=order, product=product, quantity=quantity, size=size, price=price)
                order_item.save()
            except IntegrityError:
                return Response({'error': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)

    if request.data['payment_method'] == 'online':
        return Response(ssl_response, status=status.HTTP_201_CREATED)

    return Response({'message': 'Order placed successfully!'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_user_data(request, user_id):
    user = request.user
    if user.id != user_id:
        raise PermissionDenied(
            "You are not authorized to take this action!")
    user = get_object_or_404(User, id=user_id)
    serializer = UserDataSerializer1(user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_account(request, id):
    requested_user = request.user
    if requested_user.id != id:
        raise PermissionDenied(
            "You are not authorized to take this action!")

    user = get_object_or_404(User, id=id)
    user.first_name = request.data['first_name']
    user.last_name = request.data['last_name']
    user.email = request.data['email']
    user.phone = request.data['phone']
    user.address = request.data['address']
    user.save()

    return Response({'message': 'Account edited successfully!'}, status=status.HTTP_200_OK)


class SearchList(generics.ListCreateAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        query = self.request.query_params.get('query', None)
        if query:
            qs = Product.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            ).order_by('-id')
            return qs

        return Response({'error': 'No query was provided!'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_wishlist_items(request):
    user = request.user
    qs = WishList.objects.filter(user=user).order_by('-id')
    serializer = WishListSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def if_in_wishlist(request, slug):
    user = request.user
    product = get_object_or_404(Product, slug=slug)
    qs = WishList.objects.filter(user=user, product=product)
    if qs.exists():
        return Response({'message': True}, status=status.HTTP_200_OK)
    else:
        return Response({'message': False}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_wishlist(request, slug):
    user = request.user
    product = get_object_or_404(Product, slug=slug)
    qs = WishList.objects.filter(user=user, product=product)
    if qs.exists():
        qs.delete()
        return Response({'message': 'Product removed from wishlist!'}, status=status.HTTP_200_OK)
    else:
        WishList.objects.create(user=user, product=product)
        return Response({'message': 'Product added to wishlist!'}, status=status.HTTP_201_CREATED)


class QnAList(generics.ListCreateAPIView):
    serializer_class = QnASerializer

    def get_queryset(self):
        slug = self.kwargs['slug']

        user = self.request.user
        if user.is_authenticated and (user.is_moderator or user.is_admin):
            qs = QnA.objects.filter(
                product__slug=slug
            ).order_by('-id')
            return qs

        qs = QnA.objects.filter(
            product__slug=slug
        ).exclude(
            answer__exact=None
        ).exclude(
            answer=''
        ).order_by('-id')
        return qs


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_question(request, slug):
    product = get_object_or_404(Product, slug=slug)
    user = request.user
    question = request.data['question']
    if product and user and question:
        QnA.objects.create(product=product, user=user, question=question)
        return Response({'message': 'Question added successfully!'}, status=status.HTTP_201_CREATED)

    return Response({'error': 'Something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POSt'])
@permission_classes([IsAuthenticated])
def add_answer(request, qna_id):
    user = request.user
    if user.is_admin or user.is_moderator:
        answer = request.data['answer']
        if answer:
            qna = get_object_or_404(QnA, id=qna_id)
            qna.answer = answer
            qna.save()
            return Response({'message': 'Answer added successfully!'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'No answer found!'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'You are not authorized to perform this action!'}, status=status.HTTP_400_BAD_REQUEST)


class UnansweredList(generics.ListAPIView):
    serializer_class = QnASerializer

    @permission_classes([IsAuthenticated])
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_admin or user.is_moderator:
                qs = QnA.objects.filter(Q(answer__exact=None) | Q(
                    answer__exact='')).order_by('id')

                # TODO: Send email to the user who asked the question.

                return qs
            return Response({'error': 'You are not authorized to perform this action!'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'You are not authenticated!'}, status=status.HTTP_400_BAD_REQUEST)


class OrderList(generics.ListAPIView):
    serializer_class = OrderSerializer

    @permission_classes([IsAuthenticated])
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_admin or user.is_moderator:
                qs = Order.objects.all().order_by('-id')
                return qs

            raise PermissionDenied(
                detail='You are not authorized to perform this action.')

        raise PermissionDenied(detail='You are not authenticated.')


@api_view(['GET'])
def get_order_items(request, order_id):
    qs = OrderItem.objects.filter(order__id=order_id)
    serializer = OrderItemSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_order_status(request, id):
    user = request.user
    if user.is_authenticated:
        if user.is_admin or user.is_moderator:
            status = request.data['status']
            if status:
                order = get_object_or_404(Order, id=id)
                order.status = status
                order.save()
                return Response({'message': 'Order status changed successfully!'})
            else:
                return Response({'error': 'No status found!'})
        else:
            return Response({'error': 'You are not authorized to perform this action!'})

    return Response({'error': 'You are not authenticated!'})


@api_view(['GET'])
def new_arrivals(request):
    qs = Product.objects.all().order_by('-id')[:12]
    serializer = ProductSerializer(qs, many=True)
    return Response(serializer.data)

# track orders


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_orders(request):
    user = request.user
    if user.is_authenticated:
        qs = Order.objects.filter(username=user.username).order_by('-id')
        serializer = OrderSerializer(qs, many=True)
        return Response(serializer.data)
    else:
        return Response({'error': 'You are not authenticated!'})


@api_view(['GET'])
def get_moderators(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            qs = User.objects.filter(is_moderator=True)
            serializer = UserDataSerializer1(qs, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'You are not authorized!'})
    else:
        return Response({'error': 'You are not logged in!'})


@api_view(['PUT'])
def change_moderator_status(request, user_id):
    if request.user.is_authenticated:
        if request.user.is_admin:
            user = get_object_or_404(User, id=user_id)
            user.is_moderator = not user.is_moderator
            user.save()
            return Response({'message': 'Moderator status changed successfully!'})
        else:
            return Response({'error': 'You are not authorized!'})
    else:
        return Response({'error': 'You are not logged in!'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request, query):
    if request.user.is_admin and query != None:
        qs = User.objects.filter(Q(username__icontains=query) |
                                 Q(email__icontains=query) |
                                 Q(first_name__icontains=query) |
                                 Q(last_name__icontains=query)
                                 ).exclude(
            is_moderator=True
        )[:20]
        serializer = UserDataSerializer1(qs, many=True)
        return Response(serializer.data)


@api_view(['POST'])
def change_pass_test(request):
    print(request.user)
    user = User.objects.get(username=request.user.username)
    new_pass = request.data['new_pass']
    user.set_password(new_pass)
    user.save()
    return Response({'message': 'Password changed successfully!'})
