from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import CharField
from django.utils import timezone
from uuid import uuid4

from store_app.api import validators 

# Create your models here.

DEFAULT_VARCHAR_SIZE = 255
DEFAULT_TEXT_SIZE = 5000

class Promotion(models.Model):
    class Meta:
        db_table = 'promotions'

    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)
    discount = models.IntegerField(null=True, blank=True)
    expire_at = models.DateTimeField(null=True, blank=True)

class Tag(models.Model):
    class Meta:
        db_table = 'tags'

    created_at = models.DateTimeField(auto_now_add=True)
    label = models.CharField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)

class Collection(models.Model):
    class Meta:
        db_table = 'collections'

    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)
    description = models.TextField(max_length=DEFAULT_TEXT_SIZE, null=True, blank=True)
    featured_product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    def __str__(self) -> CharField:
        return self.title

class Product(models.Model):
    class Meta:
        db_table = 'products'
        ordering = ['title']

    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    description = models.TextField(max_length=DEFAULT_TEXT_SIZE, null=True, blank=True)
    price = models.FloatField(blank=True, null=True)
    inventory = models.IntegerField(validators=[MinValueValidator(1)])
    collection = models.ForeignKey(
        Collection, on_delete=models.PROTECT, related_name='products')
    promotions = models.ManyToManyField(Promotion, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

class ProductImage(models.Model):
    class Meta:
        db_table = 'product_images'
    
    created_at = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='api/images',
                            validators=[validators.validate_file_size])

class Order(models.Model):
    class Meta:
        db_table = 'orders'
        permissions = [
            ('cancel_order', 'Can Cancel Order')
        ]

    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed'),
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    payment_status = models.CharField(blank=True, null=True, max_length=DEFAULT_VARCHAR_SIZE, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    customer_name =  models.CharField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)
    customer_email =  models.EmailField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)

class OrderItem(models.Model):
    class Meta:
        db_table = 'order_items'

    placed_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name='items')
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='orderitems')
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.FloatField(blank=True, null=True)

class Cart(models.Model):
    class Meta:
        db_table = 'carts'

    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    customer_name =  models.CharField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)
    customer_email =  models.EmailField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)

class CartItem(models.Model):
    class Meta:
        db_table = 'cart_items'
        unique_together = [['cart', 'product']]

    created_at = models.DateTimeField(auto_now_add=True)
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        unique_together = [['cart', 'product']]

class Review(models.Model):
    class Meta:
        db_table = 'reviews'

    created_at = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews')
    customer_name =  models.CharField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)
    customer_email =  models.EmailField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)
    comment = models.TextField(max_length=DEFAULT_TEXT_SIZE, blank=True, null=True)
    rating = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(5)]
    )

class Shipping(models.Model):
    class Meta:
        db_table = 'shippings'

    SHIPPING_STATUS_ORDER_PLACED = 'OP'
    SHIPPING_STATUS_ON_HOLD = 'ON'
    SHIPPING_STATUS_SHIPPED = 'S'
    SHIPPING_STATUS_IN_TRANSIT = 'IT'
    SHIPPING_STATUS_DELIVERED = 'D'
    SHIPPING_STATUS_CANCELED = 'C'
    SHIPPING_STATUS_RETURNED = 'R'

    SHIPPING_STATUS_CHOICES = [
        (SHIPPING_STATUS_ORDER_PLACED, 'Order Placed'),
        (SHIPPING_STATUS_ON_HOLD, 'On Hold'),
        (SHIPPING_STATUS_SHIPPED, 'Shipped'),
        (SHIPPING_STATUS_IN_TRANSIT, 'In Transit'),
        (SHIPPING_STATUS_DELIVERED, 'Delivered'),
        (SHIPPING_STATUS_CANCELED, 'Canceled'),
        (SHIPPING_STATUS_RETURNED, 'Returned'),
    ]

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE)
    shipping_status = models.CharField(blank=True, null=True, max_length=DEFAULT_VARCHAR_SIZE, choices=SHIPPING_STATUS_CHOICES, default=SHIPPING_STATUS_ORDER_PLACED)
    shipping_method = models.CharField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)
    placed_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    estimate_delivery_date = models.DateTimeField(null=True, blank=True)
    customer_name =  models.CharField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)
    customer_email =  models.EmailField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)
    customer_number = models.CharField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)
    city = models.CharField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)
    state = models.CharField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)
    country = models.CharField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)
    zip = models.SmallIntegerField(null=True, blank=True)

class Payment(models.Model):
    class Meta:
        db_table = 'payments'

    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed'),
    ]

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE)
    payment_status = models.CharField(blank=True, null=True, max_length=DEFAULT_VARCHAR_SIZE, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    payment_method = models.CharField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    customer_name =  models.CharField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)
    customer_email =  models.EmailField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)
    price = models.FloatField(blank=True, null=True)
    