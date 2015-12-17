
from django.shortcuts import render
from django.http import HttpResponse
from models import *

import cities_dictionary
import aggregator
import time
import json

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
            return render(request,'project/index.html', {"message": "The login information entered is incorrect."})

    return render(request, 'project/index.html')

def register(request):
    if request.method == 'POST':
        success = register_user(request)
        if success:
            return render(request,'project/dashboard.html')
        else:
            #Someone has to make the HTML to handle incorrect login
            print 'Handle if user is registered already'
            return render(request,'project/register.html', {"message": "This user is registered already."})

    return render(request, 'project/register.html')

def dashboard(request):
    #Get current user's searches and fetch results from mongo tables
    #Refresh HTML table with results

    return render(request, 'project/dashboard.html')

def monitordash(request):
    #show monitoring information
    return render(request, 'project/monitordash.html')

def register_user(request):
    email    = request.POST['regemail'].strip()
    password = request.POST['regpw'].strip()

    try:
        user = Users.objects.get(email = email)
        print 'User Already Registered'
        return False

    except Users.DoesNotExist:
        new_user = Users.objects.create(email = email, password = password, ebay_search = [], craigslist_search = [])
        print 'New User Added!'
        return new_user.user_id

def login_user(request):
    email    = request.POST['email'].strip()
    password = request.POST['password'].strip()

    try:
        user = Users.objects.get(email = email, password = password)
        print 'User Logged in'
        return user.user_id

    except Users.DoesNotExist:
        print 'Incorrect login'
        return False

def data_analysis(request):
    #require a filter to use service
    #display most recent searches
    if request.GET['filter'] == "time":
    	Ebay_results=Ebay_Item.objects.order_by('-time_created')[:10]
    	Craig_results=Craigslist_Item.objects.order_by('-time_created')[:10]
    	results={}
	
	c_count=0
	e_count=0

	for c_item in Craig_results:
            results['item'+str(c_count)] = {'title':c_item.title, 'url':c_item.url, 'time':'$'+str(c_item.time_created)}
            c_count = c_count + 1

        for e_item in Ebay_results:
            results['item'+str(e_count)] = {'title':e_item.title, 'url':e_item.url, 'time':'$'+str(e_item.time_created)}
            e_count = e_count + 1

    	print json.dumps(results, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
    	#return(render, 'project/monitordash.html', {"message":'Results by time'}) 
        #return(render, 'project/monitordash.html')

    #display most expensive items
    if request.GET['filter'] == "price":
        Ebay_results=Ebay_Item.objects.order_by('-price')[:10]
        Craig_results=Craigslist_Item.objects.order_by('-price')[:10]
        results={}

        c_count=0
        e_count=0

        for c_item in Craig_results:
            results['item'+str(c_count)] = {'title':c_item.title, 'url':c_item.url, 'price':'$'+str(c_item.price)}
            c_count = c_count + 1

        for e_item in Ebay_results:
            results['item'+str(e_count)] = {'title':e_item.title, 'url':e_item.url, 'price':'$'+str(e_item.price)}
            e_count = e_count + 1

        print json.dumps(results, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
        #return(render, 'project/monitordash.html',{"message":'Results by time'})
        #return(render, 'project/monitordash.html')

    return render(request, 'project/monitordash.html')
    
def scrape_data(request):
    if request.GET['term']:
        keyword = unicode(str.lower(str(request.GET['term'])))
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
    user = '5671d336b2b851092976a0da'

    #Rough Cache - Not too good, needs work
    try:
        print 'Checking Cache'
        search1 = Craigslist_Search.objects.get(keyword = keyword, city = city, min_price__lte = int(min_price), max_price__gte = int(max_price))
        search2 = Ebay_Search.objects.get(keyword = keyword, min_price__lte = int(min_price), max_price__gte = int(max_price))

        results = {}

        c_count = 0
        e_count = 0

        for c_item in Craigslist_Item.objects.all().filter(keyword = keyword, city__in = search1.near_cities, price__range = (int(min_price), int(max_price))):
            results['item'+str(c_count)] = {'title':c_item.title, 'url':c_item.url, 'price':'$'+str(c_item.price)} 
            c_count = c_count + 1

        for e_item in Ebay_Item.objects.all().filter(keyword = keyword, price__range = (int(min_price), int(max_price))):
            results['item'+str(e_count)] = {'title':e_item.title, 'url':e_item.url, 'price':'$'+str(e_item.price)}
            e_count = e_count + 1

        try:
            user = Users.objects.get(user_id = user_key)
            if search1 not in user.craigslist_search:
                user.craigslist_search.append(search1)
                print "Added Craigslist_Search to: " + user.email
            if search2 not in user.ebay_search:
                user.ebay_search.append(search2)
                print "Added Ebay_Search to: " + user.email
        except User.DoesNotExist:
            pass

        print json.dumps(results, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
        
        return render(request, 'project/dashboard.html', {"message":'CACHED'})
       
    except (Craigslist_Search.MultipleObjectsReturned, Ebay_Search.MultipleObjectsReturned, Craigslist_Search.DoesNotExist, Ebay_Search.DoesNotExist) as e:
        print 'Cache Miss: Scrapping'
        aggregator.scrape_data(keyword,max_price,min_price,request.GET['citydrop'],user)

        while True:
            try:
                ebay_search = Ebay_Search.objects.get(keyword = keyword, min_price = int(min_price), max_price = int(max_price)) 
                craigslist_search = Craigslist_Search.objects.get(keyword = keyword, city = city, min_price = int(min_price),max_price = int(max_price)) 
            
                results = {}

                c_count = 0
                e_count = 0

                for c_item in Craigslist_Item.objects.all().filter(keyword = keyword, city__in = craigslist_search.near_cities, price__range = (int(min_price), int(max_price))):
                    results['item'+str(c_count)] = {'title':c_item.title, 'url':c_item.url, 'price':'$'+str(c_item.price)}
                    c_count = c_count + 1

                for e_item in Ebay_Item.objects.all().filter(keyword = keyword, price__range = (int(min_price), int(max_price))):
                    results['item'+str(e_count)] = {'title':e_item.title, 'url':e_item.url, 'price':'$'+str(e_item.price)}
                    e_count = e_count + 1                

                print json.dumps(results, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))                
                
                return render(request, 'project/dashboard.html', {"message":'SCRAPPED'})
            except (Ebay_Search.DoesNotExist, Craigslist_Search.DoesNotExist) as e:
                time.sleep(.5)
    
    return render(request, 'project/dashboard.html', {"message":"OTHER - THIS SHOULD NEVER HAPPEN!"})
