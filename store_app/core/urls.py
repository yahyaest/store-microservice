from django.urls import path, include

from store_app.core.views import home_page, htmx_http, htmx_page, login_page, product_page, products_page, cart_page, notifications_page, unread_notifications_page, logout_view, register_page, submit_product_review, create_or_update_cart, edit_cart_item, delete_cart, delete_selected_cart_items

urlpatterns = [
    path('', home_page, name='home'),
    path('htmx', htmx_page, name='htmx'),
    path('htmx/http', htmx_http, name='htmx_http'),
    path('login', login_page, name='login'),
    path('register', register_page, name='register'),
    path('logout', logout_view, name='logout'),
    path('products', products_page, name='products'),
    path('product/<slug:slug>/', product_page, name='product'),
    path('cart', cart_page, name='cart'),
    path('notifications', notifications_page, name='notifications'),
    path('unread_notifications', unread_notifications_page, name='unread_notifications'),
    path('submit-review', submit_product_review, name='submit-review'),
    path('create-or-update-cart', create_or_update_cart, name='create-or-update-cart'),
    path('edit_cart_item', edit_cart_item, name='edit_cart_item'),
    path('delete_cart', delete_cart, name='delete_cart'),
    path('delete_selected_cart_items', delete_selected_cart_items, name='delete_selected_cart_items'),
]
