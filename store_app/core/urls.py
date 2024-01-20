from django.urls import path, include

from store_app.core.views import home_page, product_page, products_page

urlpatterns = [
    path('', home_page, name='home'),
    path('products', products_page, name='products'),
    path('product/<slug:slug>/', product_page, name='product')
]
