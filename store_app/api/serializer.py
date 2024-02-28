from rest_framework import serializers
import datetime
import pytz
from .models import Cart, CartItem, Collection, Order, OrderItem, Payment, Product, ProductImage, Promotion, Review, Shipping, Tag
from django.db import transaction
from .signals import order_created
import traceback
from store_app.tools.helpers import *

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'created_at', 'title', 'description', 'products_count']

    products_count = serializers.IntegerField(read_only=True)

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'created_at', 'label']

class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ['id', 'created_at', 'last_update', 'description', 'discount', 'expire_at']

class ProductImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id, **validated_data)

    class Meta:
        model = ProductImage
        fields = ['id', 'created_at', 'image']

class ProductSerializer(serializers.ModelSerializer):
    product_images = serializers.ListField(required=False, allow_null=False)
    product_tags = serializers.ListField(required=False, allow_null=False)
    product_promotions = serializers.ListField(required=False, allow_null=False)

    class Meta:
        model = Product
        fields = ('id', 'created_at', 'last_update', 'title', 'slug', 'description', 'inventory',
                    'price', 'price_with_tax', 'collection', 'external_args', 'product_images', 'product_tags', 'product_promotions')

    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')

    def calculate_tax(self, product: Product):
        return product.price * 1.1
    
    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError as exc:
            # Log the validation errors
            logger.error(f"Validation error during deserialization: {exc.detail}")
            raise exc
    
    def create(self, validated_data):
        try:
            product_images = validated_data.pop('product_images', [])
            product_tags = validated_data.pop('product_tags', [])
            product_promotions = validated_data.pop('product_promotions', [])

            with transaction.atomic():

                # Create the Product instance without images and tags
                product_instance = Product.objects.create(**validated_data)

                # Get the id of the newly created Product instance
                product_id = product_instance.id

                # Create ProductImage instances and associate them with the product
                for product_image in product_images:
                    image_data = {"product": product_instance, "image": product_image}
                    ProductImage.objects.create(**image_data)

                # Create Tag instances and associate them with the product
                tags_instances = []
                for product_tag in product_tags:
                    tag_data = {"label" : product_tag}
                    tag_instance, created = Tag.objects.get_or_create(**tag_data)
                    tags_instances.append(tag_instance)

                product_instance.tags.set(tags_instances)

                # Create Promotion instances and associate them with the product
                promotions_instances = []
                for product_promotion in product_promotions:
                    promotion_instance, created = Promotion.objects.get_or_create(**product_promotion)
                    promotions_instances.append(promotion_instance)

                product_instance.promotions.set(promotions_instances)

            return product_instance
        
        except Exception as e:
            logger.error(f"{traceback.format_exc()}")
            raise e

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'created_at', 'last_update', 'customer_name', 'customer_email', 'customer_image', 'comment', 'rating']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)
    
class SimpleProductSerializer(serializers.ModelSerializer):
    background_image = serializers.CharField(source='external_args.background_image', allow_null=True, allow_blank=True)
    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'inventory', 'background_image']

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()
    total_price_after_discount = serializers.SerializerMethodField()

    def get_total_price_after_discount(self, cart_item: CartItem):
        product_promotions = cart_item.product.promotions.all()
        promotion_expiration_date = product_promotions[0].expire_at if product_promotions else None
        if promotion_expiration_date and promotion_expiration_date > datetime.datetime.now(pytz.timezone('UTC')):
            return cart_item.quantity * cart_item.product.price * (1 - product_promotions[0].discount/100)
        else:
            return cart_item.quantity * cart_item.product.price

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.price

    class Meta:
        model = CartItem
        fields = ['id', 'created_at', 'product', 'quantity', 'total_price', 'total_price_after_discount']

class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    total_price_after_discount = serializers.SerializerMethodField()

    def get_items_count(self, cart):
        return sum([item.quantity for item in cart.items.all()])

    def get_total_price_after_discount(self, cart):
        total_price = 0
        for item in cart.items.all():
            product_promotions = item.product.promotions.all()
            promotion_expiration_date = product_promotions[0].expire_at if product_promotions else None
            if promotion_expiration_date and promotion_expiration_date > datetime.datetime.now(pytz.timezone('UTC')):
                total_price = total_price + item.quantity * item.product.price * (1 - product_promotions[0].discount/100)
            else:
                total_price = total_price + item.quantity * item.product.price
        return total_price

    def get_total_price(self, cart):
        return sum([item.quantity * item.product.price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'last_update', 'items', 'items_count', 'total_price', 'total_price_after_discount']

class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value):
            raise serializers.ValidationError(
                'No product with the given ID is found')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(
                cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'placed_at', 'product', 'unit_price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'placed_at', 'last_update', 'payment_status', 'customer_name', 'customer_email', 'items']


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError(
                'No cart with the given ID was Found ❌')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('Cart is empty 💢')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']

            order = Order.objects.create(customer_name= self.validated_data['customer_name'])

            cart_items = CartItem.objects \
                .select_related('product') \
                .filter(cart_id=cart_id)
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
                ) for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(pk=cart_id).delete()

            order_created.send_robust(sender=self.__class__, order=order)

            return order
        

class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = ['id', 'order', 'shipping_status', 'shipping_method', 'placed_at', 'delivered_at','estimate_delivery_date', 'customer_name', 'customer_email', 'customer_number', 'city', 'state', 'country', 'zip']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'payment_status', 'payment_method', 'payment_date', 'customer_name', 'customer_email', 'price']