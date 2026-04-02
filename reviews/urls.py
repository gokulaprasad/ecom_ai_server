from django.urls import path
from .views import (
    ProductReviewsView, CreateReviewView, UpdateReviewView,
    MarkReviewHelpfulView, UserReviewsView
)

urlpatterns = [
    # Product reviews
    path('product/<str:product_slug>/', ProductReviewsView.as_view(), name='product-reviews'),
    path('product/<str:product_slug>/create/', CreateReviewView.as_view(), name='create-review'),
    
    # User reviews
    path('my-reviews/', UserReviewsView.as_view(), name='my-reviews'),
    
    # Review actions
    path('<str:review_id>/', UpdateReviewView.as_view(), name='update-review'),
    path('<str:review_id>/helpful/', MarkReviewHelpfulView.as_view(), name='mark-helpful'),
]
