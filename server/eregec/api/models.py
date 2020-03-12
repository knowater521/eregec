from django.db import models

class UserInfo(models.Model):
    username = models.CharField(primary_key=True, max_length=128)
    name = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    sex = models.BooleanField()
    tel = models.CharField(max_length=128)

class PlatformInfo(models.Model):
    username = models.CharField(primary_key=True, max_length=128)
    name = models.CharField(max_length=128)