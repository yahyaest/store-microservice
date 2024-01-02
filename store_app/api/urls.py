from rest_framework_nested import routers
from .views import CartItemViewSet, CartViewSet, CollectionViewSet, OrderViewSet, PaymentViewSet, ProductImageViewSet, ProductViewSet, PromotionViewSet, ReviewViewSet, ShippingViewSet, TagViewSet

router = routers.DefaultRouter()

router.register('products', ProductViewSet, basename='products')
products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('images', ProductImageViewSet,basename='product-images')
products_router.register('reviews', ReviewViewSet, basename='product-reviews')

router.register('carts', CartViewSet)
carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', CartItemViewSet, basename='cart-items')

router.register('collections', CollectionViewSet)
router.register('orders', OrderViewSet, basename='orders')
router.register('tags', TagViewSet)
router.register('promotions', PromotionViewSet)
router.register('shippings', ShippingViewSet)
router.register('payments', PaymentViewSet)

urlpatterns = router.urls + products_router.urls + carts_router.urls