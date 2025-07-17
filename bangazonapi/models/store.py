"""Store model"""

from django.db import models
from .customer import Customer
from django.contrib.auth import get_user_model

User = get_user_model()

class Store(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
