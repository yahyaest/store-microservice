import json
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg
from django.middleware.csrf import get_token
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django_htmx.http import HttpResponseClientRedirect, HttpResponseClientRefresh, HttpResponseLocation, HttpResponseStopPolling, push_url, reswap, retarget, trigger_client_event
from store_app.clients.gateway import Gateway
from store_app import settings
from store_app.core.forms import HtmxForm, LoginForm, RegisterForm, ReviewForm
from store_app.api.models import Product, ProductImage, Review
from store_app.tools.helpers import *
from datetime import datetime
import pytz

def getUserToken(request):
    cookies_obj = {}
    cookies_str : str = request.headers.get('Cookie', None)
    if cookies_str :
        cookies_list = cookies_str.split(";")
        for cookie in cookies_list:
            key = cookie.split("=")[0].strip()
            try:
                import ast
                value = ast.literal_eval(cookie.split("=")[1].strip())
                value = json.loads(value)
            except :
                value = cookie.split("=")[1].strip()
            cookies_obj[f'{key}'] = value
        return cookies_obj
    return None


def is_promotion_not_expired(game_promotion_expiration_date: str) -> bool:
    current_date = datetime.now(pytz.UTC)
    date1 = current_date
    date2 = game_promotion_expiration_date

    if date1 < date2:
        return True
    return False


# Create your views here.
def htmx_page(request):
    logger.info(f"htmx request is : {request.htmx.__dict__}")
    # Get htmx http operation
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        logger.info(f" data is : {data}")
        with open('./store_app/core/operation.txt', 'w') as file:
            file.write(data['operation'])

    if request.htmx:
        logger.info("HTMX Request")
        if request.htmx.trigger:
            logger.info(f"htmx request target is : {request.htmx.target}")
            logger.info(f"htmx.trigger request trigger is : {request.htmx.trigger}")

            operation = None
            with open('./store_app/core/operation.txt', 'r') as file:
                operation = file.read()
            logger.info(f" operation is : {operation}")

            if operation == 'reswap':
                response = render(request=request, template_name='partials/partial_htmx.html')
                return reswap(response, 'beforeend')
            elif operation == 'retarget':
                form = HtmxForm(request.GET)
                if form.is_valid():
                    response =  HttpResponse("Form is valid !!!")
                    return trigger_client_event(response, "htmx-added")
                else:
                    context = {"form" : form}
                    response = render(request=request, template_name='partials/partial_htmx_form.html', context=context)
                    return retarget(response, "#main-content")
                    form_errors = form.errors
                    logger.error(f"form_errors are : {form_errors}")
                    return HttpResponse(f"Form is invalid !!!. {form_errors}")
            else:
                return render(request=request, template_name='partials/partial_htmx.html')
        else:
            operation = None
            with open('./store_app/core/operation.txt', 'r') as file:
                operation = file.read()
            logger.info(f" operation is : {operation}")
            
            if operation == 'redirect':
                return HttpResponseClientRedirect("/admin/")
            elif operation == 'refresh':
                return HttpResponseClientRefresh()
            if operation == 'location-page':
                return HttpResponseLocation("/product/red-dead-redemption-2/")
            if operation == 'location-div':
                return HttpResponseLocation("/api/products/14/", target="#htmx-swap")
            elif operation == 'stop-polling':
                return htmx_http(request)
            elif operation == 'push-url':
                response = render(request=request, template_name='partials/partial_htmx.html')
                return push_url(response, '/htmx/lorem')
            else:
                logger.info("Nothing to do")
                return HttpResponse("Nothing to do !!!")
    else:
        logger.info("Not an HTMX Request")
        context = {"form" : HtmxForm()}
        return render(request=request, template_name='htmx.html', context=context)

def htmx_http(request):
    # rand = random.random()
    # logger.info(f" rand is : {rand}")
    # if rand < 0.35:
    #     return HttpResponseStopPolling()
    with open('./store_app/core/operation.txt', 'r') as file:
        operation = file.read()
        logger.info(f" operation is : {operation}")
        if operation == 'stop-polling':
            return HttpResponseStopPolling()
    return HttpResponse("HTMX HTTP Response !!!")

def home_page(request):
    return render(request=request, template_name='home.html')

def login_page(request):
    # If token in cookies redirect home
    cookies = getUserToken(request)
    if cookies and cookies.get('token', None):
        response = HttpResponseRedirect('/')
        return response
    
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            data = {"email":email,"password": password}
            gateway = Gateway()
            token,error = gateway.login(data)
            if token:
                logger.info(f"token is : {token}")
                current_user = gateway.get_current_user()
                current_user_image = gateway.get_current_user_image()
                if current_user_image:
                    current_user["avatarUrl"] = current_user_image['filename']
                logger.info(f"current_user is : {current_user}")

                response = HttpResponseRedirect('/')
                response.set_cookie("token", token, secure=True, httponly=True)
                response.set_cookie("user", json.dumps(current_user), secure=True, httponly=True)
                return response
            else:
                if error:
                    error_message = error["message"]
                return render(request, 'login.html', {'form': form, 'error_message': error_message if error_message else None})            
    else:
        form = LoginForm()
    return render(request=request, template_name='login.html',context={'form': form})

def register_page(request):
    # If token in cookies redirect home
    cookies = getUserToken(request)
    if cookies and cookies.get('token', None):
        response = HttpResponseRedirect('/')
        return response
    
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if 'image' in request.FILES:
            form.files['image'] = request.FILES['image']
        if form.is_valid():
            try:
                email = form.cleaned_data.get('email')
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                phone = form.cleaned_data.get('phone')
                image_file = request.FILES.get('image')
                data = {
                    "email":email, 
                    "username": username, 
                    "password": password,
                    "phone": phone,
                    }
                logger.info(f"image_file is : {image_file} with type : {type(image_file)}")

                logger.info(f"image_file dict is : {image_file.__dict__}  ")
                gateway = Gateway()
                token,error = gateway.register(data)
                if token:
                    logger.info(f"token is : {token}")
                    data,error2 = gateway.upload_image(image_file, email)
                    logger.info(f"user image data is : {data}")
                    current_user = gateway.get_current_user()
                    current_user_image = gateway.get_current_user_image()
                    if current_user_image:
                        current_user["avatarUrl"] = current_user_image['filename']
                    logger.info(f"current_user is : {current_user}")

                    response = HttpResponseRedirect('/')
                    response.set_cookie("token", token, secure=True, httponly=True)
                    response.set_cookie("user", json.dumps(current_user), secure=True, httponly=True)
                    return response
                else:
                    if error:
                        error_message = error["message"]
                    return render(request, 'register.html', {'form': form, 'error_message': error_message if error_message else None})
            except forms.ValidationError as e:
                error_message = str(e)
                return render(request, 'register.html', {'form': form, 'error_message': error_message})  
        else:
            error_message = form.errors.get('password')
            logger.error(f"Form not valid : {error_message}")   
            return render(request, 'register.html', {'form': form, 'error_message': error_message})

    else:
        form = RegisterForm()
    return render(request=request, template_name='register.html', context={'form': form})

def logout_view(request):
    response = HttpResponseRedirect('/')
    response.delete_cookie("token")
    response.delete_cookie("user")
    return response

def products_page(request):
    products_list = Product.objects.all()
    pages = len(products_list) // 20 + 1
    page_range = list(range(1, pages + 1))
    paginator = Paginator(products_list, 20)

    page_number = request.GET.get('page') if request.GET.get('page') else 1
    logger.info(f"page_number is : {page_number}")
    products = paginator.get_page(page_number)
    return render(request=request, template_name='products.html',context={'products': products, 'page_range': page_range, 'current_page': int(page_number)})

def product_page(request, slug):
    user =  None
    is_user_product_review = False
    cookies = getUserToken(request)
    if cookies and cookies.get('user', None):
        user = cookies.get('user', None)
    product = get_object_or_404(Product, slug=slug)
    product_tags = product.tags.all()
    product_images = ProductImage.objects.filter(product_id=product.pk)
    product_reviews = Review.objects.filter(product_id=product.pk)
    product_promotions = product.promotions.all()
    is_promotion_valid = len(product_promotions) > 0 and is_promotion_not_expired(product_promotions[0].expire_at)
    product_price_after_discount = product.price - (product.price * product_promotions[0].discount) / 100 if is_promotion_valid else product.price

    if user:
        user_product_review = Review.objects.filter(product_id=product.pk, customer_email= user['email'])
        if len(user_product_review) > 0:
            is_user_product_review = True

    product_average_rating = product_reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
    product_average_rating = round(product_average_rating, 1) if product_average_rating else None
    gateway_base_url = settings.GATEWAY_BASE_URL
    return render(
        request=request, 
        template_name='product.html',
        context={
            'gateway_base_url':gateway_base_url,
            'user': user,
            'is_user_product_review': is_user_product_review,
            'product': product, 
            'product_tags': product_tags, 
            'product_images': product_images,
            'product_promotions': product_promotions,
            'is_promotion_valid': is_promotion_valid,
            'product_price_after_discount': product_price_after_discount,
            'product_inventory' : product.inventory,
            'product_reviews': product_reviews if product_reviews else [],
            'product_average_rating': product_average_rating if product_average_rating else 0,
            'review_form': ReviewForm()
            }
        )

@require_POST
def submit_product_review(request):
    gateway_base_url = settings.GATEWAY_BASE_URL
    user =  None
    cookies = getUserToken(request)
    if cookies and cookies.get('user', None):
        user = cookies.get('user', None)

    if user:
        rating = int(request.POST.get('rating', 1))
        product_id = int(request.POST.get('product-id', 0))

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = Review.objects.create(
                    customer_email=user['email'],
                    customer_image=user['avatarUrl'],
                    customer_name=user['username'],
                    comment=form.cleaned_data['comment'],
                    rating=rating,
                    product_id=product_id
                )

            return render(
                request=request,
                template_name='partials/product_reviews.html#reviewform-partial', 
                context = {
                    'user': user,
                    'review': review,
                    'form': form,
                    'gateway_base_url': gateway_base_url
                    }
                )
        else:
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/')