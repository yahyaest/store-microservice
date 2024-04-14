from .models import Product, Order
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