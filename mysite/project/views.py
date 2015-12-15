from django.shortcuts import render
from django.http import HttpResponse
from models import *

import cities_dictionary
import aggregator

def index(request):
    if request.method == 'POST':
        success = login_user(request)
        if success:
            #Create session here?
            print success
            return render(request,'project/dashboard.html')
        else:
            #Someone has to make the HTML to handle incorrect login
            print 'Handle if incorrect login'

    return render(request, 'project/index.html')

def register(request):
    if request.method == 'POST':
        success = register_user(request)
        if success:
            return render(request,'project/dashboard.html')
        else:
            #Someone has to make the HTML to handle incorrect login
            print 'Handle if user is registered already' 

    return render(request, 'project/register.html')

def dashboard(request):
    #Get current user's searches and fetch results from mongo tables
    #Refresh HTML table with results 
   
    return render(request, 'project/dashboard.html')

def register_user(request):
    email    = request.POST['regemail'].strip()
    username = request.POST['regun'].strip()
    password = request.POST['regpw'].strip()
   
    try:
        user = Users.objects.get(email = email,  password = password)
        print 'User Already Registered'
        return False
    
    except Users.DoesNotExist:
        new_user = Users.objects.create(name = username, email = email, password = password, ebay_search = [], craigslist_search = [])
        print 'New User Added!'
        return new_user.user_id

def login_user(request):
    email    = request.POST['email'].strip()
    username = request.POST['username'].strip()
    password = request.POST['password'].strip()

    try:
        user = Users.objects.get(email = email, password = password)
        print 'User Logged in'
        return user.user_id

    except Users.DoesNotExist:
        print 'Incorrect login'
        return False

def scrape_data(request):
    if request.GET['term']:
        keyword = request.GET['term']
    else:
        keyword = 'None'

    if request.GET['maxprice']:
        max_price = request.GET['maxprice']
    else:
        max_price = '999999'

    if request.GET['minprice']:
        min_price = request.GET['minprice']
    else:
        min_price = '0'
     
    city = cities_dictionary.get_cities().get(request.GET['citydrop'])
    user = 'tmp_user'

    #Rough Cache - Not too good, needs work 
    try:
        print 'Checking Cache'
        search1 = Craigslist_Search.objects.get(keyword = keyword, city = city, min_price__lte = int(min_price), max_price__gte = int(max_price))
        search2 = Ebay_Search.objects.get(keyword = keyword, min_price__lte = int(min_price), max_price__gte = int(max_price))
          
        for c_item in Craigslist_Item.objects.all().filter(keyword = keyword, city__in = search1.near_cities, price__range = (int(min_price), int(max_price))):
            print "CRAIGSLIST: " + c_item.title + " PRICE: " + str(c_item.price)

        for e_item in Ebay_Item.objects.all().filter(keyword = keyword, price__range = (int(min_price), int(max_price))):
            print "EBAY: " + e_item.title + " PRICE: " + str(e_item.price)

    #HAVE TO FIGURE OUT HOW TO HANDLE - TODO
    except (Craigslist_Search.MultipleObjectsReturned, Ebay_Search.MultipleObjectsReturned) as e:
        print 'Multiple Objects Returned'
       
    except (Craigslist_Search.DoesNotExist, Ebay_Search.DoesNotExist) as e:
        print 'Cache Miss: Scrapping'
        aggregator.scrape_data(keyword,max_price,min_price,city,user)

    #Think this has to be changed
    return render(request, 'project/dashboard.html')
