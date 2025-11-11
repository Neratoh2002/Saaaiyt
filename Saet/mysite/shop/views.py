from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Product, Order, OrderItem, Category

# DRF
from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from .serializers import ProductSerializer, OrderSerializer

# ---------------------
# HTML Views
# ---------------------

def product_list(request):
    products = Product.objects.select_related("category").all()
    categories = Category.objects.all()
    return render(request, "product_list.html", {"products": products, "categories": categories})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "product_detail.html", {"product": product})

def cart_view(request):
    return render(request, "cart.html")

# ---------------------
# Session Cart helpers
# ---------------------

CART_SESSION_KEY = "cart"  # структура: {product_id: quantity}

def _get_cart(session):
    return session.get(CART_SESSION_KEY, {})

def _save_cart(session, cart):
    session[CART_SESSION_KEY] = cart
    session.modified = True

def _cart_items(cart):
    # возвращаем queryset и доп. данные по количеству
    ids = [int(pid) for pid in cart.keys()]
    products = Product.objects.filter(id__in=ids)
    result = []
    for p in products:
        qty = int(cart[str(p.id)])
        result.append({"product": p, "quantity": qty, "subtotal": p.price * qty})
    return result

# ---------------------
# API: Products
# ---------------------

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

# ---------------------
# API: Cart (session based)
# ---------------------

@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def api_cart_get(request):
    cart = _get_cart(request.session)
    items = []
    total = 0
    for pid, qty in cart.items():
        product = get_object_or_404(Product, pk=int(pid))
        subtotal = float(product.price) * int(qty)
        items.append({
            "id": product.id,
            "name": product.name,
            "price": str(product.price),
            "image_url": product.image.url if product.image else None,
            "quantity": int(qty),
            "subtotal": f"{subtotal:.2f}",
        })
        total += subtotal
    return Response({"items": items, "total": f"{total:.2f}"})


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def api_cart_add(request):
    pid = str(request.data.get("product_id"))
    qty = int(request.data.get("quantity", 1))
    cart = _get_cart(request.session)
    cart[pid] = cart.get(pid, 0) + qty
    _save_cart(request.session, cart)
    return api_cart_get(request)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def api_cart_update(request):
    pid = str(request.data.get("product_id"))
    qty = int(request.data.get("quantity", 1))
    cart = _get_cart(request.session)
    if qty <= 0:
        cart.pop(pid, None)
    else:
        cart[pid] = qty
    _save_cart(request.session, cart)
    return api_cart_get(request)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def api_cart_remove(request):
    pid = str(request.data.get("product_id"))
    cart = _get_cart(request.session)
    cart.pop(pid, None)
    _save_cart(request.session, cart)
    return api_cart_get(request)

# ---------------------
# API: Checkout -> Order
# ---------------------

@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def api_checkout(request):
    """
    Создает заказ из содержимого сессии.
    Если пользователь аутентифицирован — привяжем к пользователю.
    Для гостя ожидаем 'email' в теле запроса (минимальная валидация на фронтенде).
    """
    cart = _get_cart(request.session)
    if not cart:
        return Response({"detail": "Корзина пуста."}, status=400)

    email = request.data.get("email", "")
    order = Order.objects.create(user=request.user if request.user.is_authenticated else None,
                                 email=email)

    # перенести позиции
    for pid, qty in cart.items():
        product = get_object_or_404(Product, pk=int(pid))
        OrderItem.objects.create(
            order=order, product=product, quantity=int(qty), price=product.price
        )

    # очистить корзину
    _save_cart(request.session, {})

    serializer = OrderSerializer(order, context={"request": request})
    return Response(serializer.data, status=201)
