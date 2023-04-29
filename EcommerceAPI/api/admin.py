from django.contrib import admin
from .models import Category, Product, ProductImage, ProductSize, User, Order, OrderItem, WishList, QnA
# Register your models here.

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductSize)
admin.site.register(User)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(WishList)
admin.site.register(QnA)

