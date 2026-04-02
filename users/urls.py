from django.urls import path
from .views import (
    RegisterView, LoginView, ProfileView, ChangePasswordView,
    AddressListCreateView, AddressDetailView, UserListView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('addresses/', AddressListCreateView.as_view(), name='addresses'),
    path('addresses/<str:pk>/', AddressDetailView.as_view(), name='address-detail'),
    path('all/', UserListView.as_view(), name='user-list'),
]
