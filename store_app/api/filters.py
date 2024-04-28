from .models import Payment, Product, Order, Shipping
from django_filters.rest_framework import FilterSet

class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            'collection_id':['exact'],
            'slug':['exact'],
            'price':['gt','lt']
        }

class OrderFilter(FilterSet):
    class Meta:
        model = Order
        fields = {
            'customer_name': ['exact'],
            'customer_email' : ['exact']
        }

class ShippingFilter(FilterSet):
    class Meta:
        model = Shipping
        fields = {
            'customer_name': ['exact'],
            'customer_email' : ['exact'],
            'order_id': ['exact']
        }

class PaymentFilter(FilterSet):
    class Meta:
        model = Payment
        fields = {
            'customer_name': ['exact'],
            'customer_email' : ['exact'],
            'order_id': ['exact']
        }