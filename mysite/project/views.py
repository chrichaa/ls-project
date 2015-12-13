from django.shortcuts import render
from django.http import HttpResponse
from models import *

import aggregator

def index(request):
    return render(request, 'project/index.html')

def register(request):
    if request.method == 'POST':
        register_user(request)
    return render(request, 'project/register.html')

def dashboard(request):
    #Get current user's searches and fetch results from mongo tables
    #Refresh HTML table with results 

    return render(request, 'project/dashboard.html')

def register_user(request):
    print 'here'
    email    = request.POST['regemail'].strip()
    username = request.POST['regun'].strip()
    password = request.POST['regun'].strip()
   
    try:
        user = Users.objects.get(email = email,  password = password)
        print 'User Already Registered'
        #Someone has to make the HTML to handle incorrect login
        return render(request,'project/login_error.html')
    
    except Users.DoesNotExist:
        new_user = Users.objects.create(name = username, email = email, password = password, ebay_search = [], craigslist_search = [])
        new_user.save()
        print 'New User Added!'

        return render(request,'project/dashboard.html')

def login_user(request):
    email    = str(request.POST['email'].strip())
    username = str(request.POST['username'].strip())
    password = str(request.POST['password'].strip())

    print "LOGIN: " + email + " USERNAME: " + username + " PASSWORD: " + password

    try:
        user = Users.objects.get(email = email, name = username, password = password)
        print 'User Logged in'
        return render(request, 'project/dashboard.html')

    except Users.DoesNotExist:
        print 'Incorrect login'
        #Someone has to make the HTML to handle incorrect login
        return render(request,'project/login_error.html')

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

    #Rough Cache - Not too good, needs work 
    try:
        search = Craigslist_Search.objects.get(keyword = keyword, city = city, min_price__lte = int(min_price), max_price__gte = int(max_price))
        
        for c_item in Craigslist_Item.objects.filter(keyword = keyword, city__in = search.near_cities, price__range = (int(min_price), int(max_price))):
            print "CRAIGSLIST: " + c_item.title + " PRICE: " + c_item.price

        for e_item in Ebay_Item.objects.filter(keyword = keyword, price__range = (int(min_price), int(max_price))):
            print "EBAY: " + e_item.title + " PRICE: " + e_item.price

    #HAVE TO FIGURE OUT HOW TO HANDLE - TODO
    except Craigslist_Search.MultipleObjectsReturned:
        print 'Multiple Objects Returned'
#        for search in Craigslist_Search.objects.filter(keyword = keyword, city = city, min_price__lte = int(min_price),max_price__gte = int(max_price)):
#            print search        
    except Craigslist_Search.DoesNotExist:
        aggregator.scrape_data(keyword,max_price,min_price,city,user)

    #Think this has to be changed
    return render(request, 'project/dashboard.html')
