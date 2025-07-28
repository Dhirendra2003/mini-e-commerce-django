from django.conf import settings
from django.db import models
from products.models import Product, ProductAttachment



class Purchase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL , null=True)
    completed=models.BooleanField(default=False)
    stripe_price = models.IntegerField(default=0) # 100 * price
    timestamp = models.DateTimeField(auto_now_add=True)
    # updated = models.DateTimeField(auto_now=True)