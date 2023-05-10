from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.text import slugify

# Create your models here.
from django.contrib.auth.models import AbstractUser
from .managers import UserManager


class User(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()
    phone = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=300, blank=True, null=True)
    is_moderator = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, null=True, unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(null=False, blank=False)
    regular_price = models.FloatField(null=False, blank=False)
    discount_price = models.FloatField(null=True, blank=True)
    stock = models.IntegerField()
    slug = models.SlugField(blank=True, null=True, unique=True)
    intro_image = models.ImageField(
        upload_to="img", default=None, null=True, blank=True
    )
    sold = models.IntegerField(default=0)
    total_ratings = models.FloatField(default=0)
    total_reviews = models.IntegerField(default=0)
    avg_rating = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="img")

    def __str__(self):
        return self.product.name


# For the purpose of availability of a product, we will have a separate model for sizes and quantity of each size.


class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=10)
    available_quantity = models.IntegerField()  # of this size.

    def __str__(self):
        return self.product.name


# each order( made when 'proceed to checkout' from cart or 'buy now' from product page) will consist of one/ more than one
# purchases, if multiple products on the cart, then multiple purchases and if one product / direct buy, one purchase. there
# can be any amount of quantity of a product in a purchase.

# chances are, a signed in user may buy, or a guest,
# if signed in, we will have the data and we will show it to the user to clarify,
# else, we will porvide a form and prompt the user to fill it out and save to local storage.


class Order(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)

    # chances are the user may not be a logged in user
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=300, blank=True, null=True)

    date_ordered = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, default="Pending", null=True, blank=True)
    shipping_charge = models.FloatField(default=0.0)
    outside_comilla = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=100, default="online")
    total = models.FloatField(default=0.0)
    # if online payment.
    transaction_id = models.CharField(max_length=256, blank=True, null=True)
    # only for online payments.
    online_paid = models.BooleanField(default=False)

    def __str__(self):
        if self.first_name:
            return f"{self.first_name} {self.last_name} ordered on {self.date_ordered}"
        else:
            return f"{self.username} ordered on {self.date_ordered}"

    def formatted_date(self):
        return self.date_ordered.strftime("%H:%M:%S, %d/%m/%Y")


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    size = models.CharField(max_length=10)
    price = models.FloatField()


class WishList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} added {self.product} on {self.added_on}"


class QnA(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.question}"


# Reviews. For now only registered users can review.
# I'll have a new model for this, with user and product, that way
# I will check if the user really purchased the product or not, I wont have to check a whole lot of things to know if the
# user is elligible to review or not. I'll just check if the user has an instance of this model for this product or not.
# Once the order is confirmed and payment is done, i'll save the instance for this model.


class EligibleReviewer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} is elligible to review "{self.product.name}"'


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} reviewed {self.product} on {self.date}"


# TODO: Try to fix the date format in the backend, like travelMedia.
