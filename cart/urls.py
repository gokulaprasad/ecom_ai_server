from django.urls import path
from .views import CartView, AddToCartView, UpdateCartItemView, RemoveCartItemView, ClearCartView

urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('add/', AddToCartView.as_view(), name='add-to-cart'),
    path('items/<str:item_id>/', UpdateCartItemView.as_view(), name='update-cart-item'),
    path('items/<str:item_id>/remove/', RemoveCartItemView.as_view(), name='remove-cart-item'),
    path('clear/', ClearCartView.as_view(), name='clear-cart'),
]
