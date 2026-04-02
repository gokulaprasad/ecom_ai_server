from djongo import models
from django.conf import settings
from products.models import Product
import uuid


class Review(models.Model):
    id = models.ObjectIdField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()  # 1-5
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    helpful_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = models.DjongoManager()
    
    class Meta:
        db_table = 'reviews'
        unique_together = ['user', 'product']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.user.email} for {self.product.name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update product rating
        self.update_product_rating()
    
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        # Update product rating
        self.update_product_rating()
    
    def update_product_rating(self):
        reviews = Review.objects.filter(product=self.product)
        if reviews.exists():
            avg_rating = sum(r.rating for r in reviews) / reviews.count()
            self.product.rating = round(avg_rating, 1)
            self.product.review_count = reviews.count()
        else:
            self.product.rating = 0
            self.product.review_count = 0
        self.product.save()


class ReviewHelpful(models.Model):
    id = models.ObjectIdField(primary_key=True, default=uuid.uuid4)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = models.DjongoManager()
    
    class Meta:
        db_table = 'review_helpful'
        unique_together = ['review', 'user']
