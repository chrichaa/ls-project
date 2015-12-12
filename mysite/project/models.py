from django.db import models
from djangotoolbox.fields import ListField
from djangotoolbox.fields import EmbeddedModelField

# Create your models here.
class Users(models.Model):
	name              = models.CharField(max_length = 255)
	email             = models.EmailField()
        password          = models.CharField(max_length = 255) 
        ebay_search       = ListField(EmbeddedModelField('Ebay_Search'))
 	craigslist_search = ListField(EmbeddedModelField('Craigslist_Search'))

class Craigslist_Search(models.Model):
	keyword   = models.CharField(max_length = 255)
	city      = models.CharField(max_length = 255)
        min_price = models.CharField(max_length = 255)
        max_price = models.CharField(max_length = 255)
        items     = ListField(EmbeddedModelField('Item'))

class Ebay_Search(models.Model):
        keyword   = models.CharField(max_length = 255)
        min_price = models.CharField(max_length = 255)
        max_price = models.CharField(max_length = 255)
        items     = ListField(EmbeddedModelField('Item'))

class Item(models.Model):
	title        = models.CharField(max_length = 255)
        url          = models.CharField(max_length = 255)
        price        = models.CharField(max_length = 255)
        key          = models.CharField(max_length = 255) 
	time_created = models.DateTimeField(auto_now_add=True)
