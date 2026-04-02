from django.urls import path
from .views import (
    CategoryListView, CategoryDetailView, CategoryCreateUpdateDeleteView,
    ProductListView, ProductDetailView, ProductCreateUpdateDeleteView,
    FeaturedProductsView, RelatedProductsView
)

urlpatterns = [
    # Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/create/', CategoryCreateUpdateDeleteView.as_view(), name='category-create'),
    path('categories/<str:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<str:slug>/update/', CategoryCreateUpdateDeleteView.as_view(), name='category-update'),
    path('categories/<str:slug>/delete/', CategoryCreateUpdateDeleteView.as_view(), name='category-delete'),
    
    # Products
    path('', ProductListView.as_view(), name='product-list'),
    path('create/', ProductCreateUpdateDeleteView.as_view(), name='product-create'),
    path('featured/', FeaturedProductsView.as_view(), name='featured-products'),
    path('<str:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('<str:slug>/update/', ProductCreateUpdateDeleteView.as_view(), name='product-update'),
    path('<str:slug>/delete/', ProductCreateUpdateDeleteView.as_view(), name='product-delete'),
    path('<str:slug>/related/', RelatedProductsView.as_view(), name='related-products'),
]
