from django.db import models
from djangotoolbox.fields import ListField
from djangotoolbox.fields import EmbeddedModelField

# Create your models here.
class Users(models.Model):
    email             = models.EmailField()
    password          = models.CharField(max_length = 255)
    ebay_search       = ListField(EmbeddedModelField('Ebay_Search'))
    craigslist_search = ListField(EmbeddedModelField('Craigslist_Search'))
    user_id           = models.AutoField(primary_key=True)

class Craigslist_Search(models.Model):
    keyword      = models.CharField(max_length = 255)
    city         = models.CharField(max_length = 255)
    near_cities  = ListField()
    min_price    = models.IntegerField()
    max_price    = models.IntegerField()

class Ebay_Search(models.Model):
    keyword      = models.CharField(max_length = 255)
    min_price    = models.IntegerField()
    max_price    = models.IntegerField()

class Ebay_Item(models.Model):
    title        = models.CharField(max_length = 255)
    keyword      = models.CharField(max_length = 255)
    url          = models.CharField(max_length = 255)
    price        = models.IntegerField()
    key          = models.CharField(max_length = 255)
    time_created = models.DateTimeField(auto_now_add=True)

class Craigslist_Item(models.Model):
    title        = models.CharField(max_length = 255)
    keyword      = models.CharField(max_length = 255)
    url          = models.CharField(max_length = 255)
    price        = models.IntegerField()
    key          = models.CharField(max_length = 255)
    city         = models.CharField(max_length = 255)
    time_created = models.DateTimeField(auto_now_add=True)
