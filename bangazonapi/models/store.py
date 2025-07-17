"""Customer store model"""
from django.db import models
from django.contrib.auth.models import User

class Store(models.Model):
    name = models.CharField(max_length=100)
    seller = models.ForeignKey(User, on_delete=models.DO_NOTHING)