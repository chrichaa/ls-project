from django.shortcuts import render
from django.http import HttpResponse
from models import *
import aggregator

def index(request):
    return render(request, 'project/index.html')

def register(request):
    return render(request, 'project/register.html')

def dashboard(request):
    client = MongoClient('localhost', 27017)
    db = client.largescale

    #Get current user's searches and fetch results from mongo tables
    #Refresh HTML table with results 

    return render(request, 'project/dashboard.html')

def scrape_data(request):
    if request.GET['term']:
        keyword = request.GET['term']
    else:
        keyword = 'None'

    if request.GET['maxprice']:
        max_price = request.GET['maxprice']
    elif (int(request.GET['maxprice']) > 999999):
        max_price = '999999.99'
    else:
        max_price = '999999.99'

    if request.GET['minprice']:
        min_price = request.GET['minprice']
    else:
        min_price = '0'
    print request.GET['citydrop']

    city = 'newyork.craigslist.org'
    user = 'tmp_user'


    try:
        search = Craigslist_Search.objects.get(keyword = keyword, city = city, min_price__lte = int(min_price), max_price__gte = int(max_price))
        
        for craigslist_item in Craigslist_Item.objects.filter(keyword = keyword, city__in = search.near_cities, price__range(int(min_price), int(max_price))):
            print "CRAIGSLIST: " + craigslist_item.title + " PRICE: " + craigslist_item.price

        for ebay_item in Ebay_Item.objects.filter(keyword = keyword, price__range(int(min_price), int(max_price))):
            print "EBAY: " + ebay_item.title + " PRICE: " + ebay_item.price

    #HAVE TO FIGURE OUT HOW TO HANDLE - TODO
    except Craigslist_Search.MultipleObjectsReturned:
        print 'Multiple Objects Returned'
#        for search in Craigslist_Search.objects.filter(keyword = keyword, city = city, min_price__lte = int(min_price),max_price__gte = int(max_price)):
#            print search        
    except Craigslist_Search.DoesNotExist:
        aggregator.scrape_data(keyword,max_price,min_price,city,user)

    #Think this has to be changed
    return render(request, 'project/dashboard.html')
