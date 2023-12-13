from rest_framework_nested import routers
from .views import CollectionViewSet, ProductImageViewSet, ProductViewSet

router = routers.DefaultRouter()
router.register('products', ProductViewSet, basename='products')
router.register('collections', CollectionViewSet)

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('images', ProductImageViewSet,basename='product-images')



urlpatterns = router.urls + products_router.urls 