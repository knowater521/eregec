from django.db import models

class UserInfo(models.Model):
    username = models.CharField(primary_key=True, max_length=128)
    name = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    sex = models.BooleanField()
    tel = models.CharField(max_length=128)

class UserData(models.Model):
    username = models.CharField(max_length=128)
    userid = models.CharField(max_length=128, default='')
    dataok = models.BooleanField(default=False)
    commandok = models.BooleanField(default=False)
    imageok = models.BooleanField(default=False)

class Data(models.Model):
    username = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    iscurrent = models.BooleanField(default=True)
    type = models.IntegerField(default=0)
    timestamp = models.IntegerField(default=0)
    value = models.CharField(max_length=128)

class Command(models.Model):
    username = models.CharField(max_length=128)
    value = models.CharField(max_length=128)

class PlatformInfo(models.Model):
    username = models.CharField(primary_key=True, max_length=128)
    name = models.CharField(max_length=128)