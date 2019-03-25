from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class OAuth_ex(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uid = models.CharField(max_length=100,default='')
    type = models.CharField(max_length=1,default='1')
