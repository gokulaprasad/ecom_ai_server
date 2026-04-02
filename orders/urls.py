from django.urls import path
from .views import (
    OrderListView, OrderDetailView, PlaceOrderView, CancelOrderView,
    AdminOrderListView, AdminOrderDetailView, UpdateOrderStatusView
)

urlpatterns = [
    # Customer endpoints
    path('', OrderListView.as_view(), name='order-list'),
    path('place/', PlaceOrderView.as_view(), name='place-order'),
    path('<str:order_number>/', OrderDetailView.as_view(), name='order-detail'),
    path('<str:order_number>/cancel/', CancelOrderView.as_view(), name='cancel-order'),
    
    # Admin endpoints
    path('admin/all/', AdminOrderListView.as_view(), name='admin-order-list'),
    path('admin/<str:order_number>/', AdminOrderDetailView.as_view(), name='admin-order-detail'),
    path('admin/<str:order_number>/status/', UpdateOrderStatusView.as_view(), name='update-order-status'),
]
