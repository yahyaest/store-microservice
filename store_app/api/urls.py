from rest_framework_nested import routers
from .views import CartItemViewSet, CartViewSet, CollectionViewSet, OrderItemViewSet, OrderViewSet, PaymentViewSet, ProductImageViewSet, ProductViewSet, PromotionViewSet, ReviewViewSet, ShippingViewSet, TagViewSet

router = routers.DefaultRouter()

router.register('products', ProductViewSet, basename='products')
products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('images', ProductImageViewSet,basename='product-images')
products_router.register('reviews', ReviewViewSet, basename='product-reviews')

router.register('carts', CartViewSet, basename='carts')
carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', CartItemViewSet, basename='cart-items')

router.register('orders', OrderViewSet, basename='orders')
orders_router = routers.NestedDefaultRouter(router, 'orders', lookup='order')
orders_router.register('items', OrderItemViewSet, basename='order-items')

router.register('collections', CollectionViewSet)
router.register('tags', TagViewSet)
router.register('promotions', PromotionViewSet)
router.register('shippings', ShippingViewSet)
router.register('payments', PaymentViewSet)

urlpatterns = router.urls + products_router.urls + carts_router.urls + orders_router.urls