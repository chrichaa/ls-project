from django.db import models
from djangotoolbox.fields import ListField
from djangotoolbox.fields import EmbeddedModelField

# Create your models here.
class User(models.Model):
	name       = models.CharField(max_length = 255)
	email      = models.EmailField()
        password   = models.CharField(max_length = 255) 
        ebay       = ListField(EmbeddedModelField('Ebay_Search'))
	craigslist = ListField(EmbeddedModelField('Craigslist_Search'))

class Craigslist_Search(models.Model):
	keyword   = models.CharField(max_length = 255)
	city      = models.CharField(max_length = 255)
        min_price = models.IntegerField()
        max_price = models.IntegerField()
        items     = ListField(EmbeddedModelField('Item'))

class Ebay_Search(models.Model):
        keyword   = models.CharField(max_length = 255)
        min_price = models.IntegerField()
        max_price = models.IntegerField()
        items     = ListField(EmbeddedModelField('Item'))

class Item(models.Model):
	title        = models.CharField(max_length = 255)
        url          = models.CharField(max_length = 255)
        price        = models.IntegerField()
        key          = models.CharField(max_length = 255) 
	time_created = models.DateTimeField(auto_now_add=True)
