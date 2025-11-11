from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    product_list, product_detail, cart_view,
    ProductViewSet,
    api_cart_get, api_cart_add, api_cart_update, api_cart_remove, api_checkout
)

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")

urlpatterns = [
    # HTML
    path("", product_list, name="product_list"),
    path("product/<int:pk>/", product_detail, name="product_detail"),
    path("cart/", cart_view, name="cart"),

    # API
    path("api/", include(router.urls)),
    path("api/cart/", api_cart_get, name="api_cart_get"),
    path("api/cart/add/", api_cart_add, name="api_cart_add"),
    path("api/cart/update/", api_cart_update, name="api_cart_update"),
    path("api/cart/remove/", api_cart_remove, name="api_cart_remove"),
    path("api/checkout/", api_checkout, name="api_checkout"),
]
