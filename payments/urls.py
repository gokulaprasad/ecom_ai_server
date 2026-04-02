from django.urls import path
from .views import (
    ProcessPaymentView, PaymentDetailView, 
    OrderPaymentView, UserPaymentsView
)

urlpatterns = [
    path('process/', ProcessPaymentView.as_view(), name='process-payment'),
    path('my-payments/', UserPaymentsView.as_view(), name='my-payments'),
    path('<str:payment_id>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('order/<str:order_number>/', OrderPaymentView.as_view(), name='order-payment'),
]
