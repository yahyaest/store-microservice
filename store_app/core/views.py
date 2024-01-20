from django.shortcuts import render, get_object_or_404
from django.db.models import Avg
from store_app.api.models import Product, ProductImage, Review

# Create your views here.
def home_page(request):
    return render(request=request, template_name='home.html')

def products_page(request):
    products = Product.objects.all()
    return render(request=request, template_name='products.html',context={'products': products})

def product_page(request, slug):
    product = get_object_or_404(Product, slug=slug)
    product_tags = product.tags.all
    product_images = ProductImage.objects.filter(product_id=product.pk)
    product_reviews = Review.objects.filter(product_id=product.pk)
    product_average_rating = product_reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
    product_average_rating = round(product_average_rating, 1) if product_average_rating else None
    return render(
        request=request, 
        template_name='product.html',
        context={
            'product': product, 
            'product_tags': product_tags, 
            'product_images': product_images,
            'product_reviews': product_reviews,
            'product_average_rating': product_average_rating
            }
        )
