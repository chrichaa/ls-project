from bson import json_util
from django.shortcuts import render
from django.http import HttpResponse
from models import *
from operator import itemgetter

import cities_dictionary
import aggregator
import time
import json
import collections
import operator

'''
|||||||||||||||||||| Index.html ||||||||||||||||||||
    When a user logs in, login_user is called. 
    Then check if they have any searches, so we can populate the tables in dashboard with their most recent searches.
    Then set the cookie.
    Return dashboard.html
||||||||||||||||||||||||||||||||||||||||||||||||||||
'''
def index(request):
    if request.method == 'POST':
        success = login_user(request)
        if success:
            print 'User ID: ' + success
           
            if not Users.objects.get(user_id = success).craigslist_search:
                response = render(request, 'project/dashboard.html')
            else:
                results = get_updated_results(Users.objects.get(user_id = success).craigslist_search[0], Users.objects.get(user_id = success).ebay_search[0], success)
                response = render(request,'project/dashboard.html',{'user_searches':Users.objects.get(user_id = success).craigslist_search, 'result_list':results})
            response.set_cookie('id',success)

            return response
        else:
            return render(request,'project/index.html', {"message": "The login information entered is incorrect."})

    return render(request, 'project/index.html')

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

'''
|||||||||||||||||||| Register.html ||||||||||||||||||||
    When a user registers, check if email is already in the database.
    If it is not, then call register_user.
    Create the new user in the Users table, and set the cookie
    Return dashboard.html
|||||||||||||||||||||||||||||||||||||||||||||||||||||||
'''

def register(request):
    if request.method == 'POST':
        success = register_user(request)
        if success:
            response = render(request,'project/dashboard.html')
            response.set_cookie('id',success)

            return response
        else:
            print 'Handle if user is registered already'
            return render(request,'project/register.html', {"message": "This user is registered already."})

    return render(request, 'project/register.html')

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

'''
|||||||||||||||||||| dashboard.html ||||||||||||||||||||
    When a user searches, call scrape_data
    First check if search already exists in table. 
        If it does, then don't scrape.
        If it doesn't, then scrape, and wait for it to finish.
    After we find results, add the search to the user's craigslist_search and ebay_search lists
    Then, call get_results, which returns a dictionary of all the search results
    Return dashboard.html with the results
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||
'''
def dashboard(request):
    return render(request, 'project/dashboard.html')

def scrape_data(request):
    if request.GET['term']:
        keyword = str.lower(str(request.GET['term']))
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
    
    if request.COOKIES.has_key('id'):
        key = request.COOKIES['id']
    else:
        key = 'None'

    timed_out = False

    try:
        print 'Checking Cache'
        craigslist_search = Craigslist_Search.objects.get(keyword = keyword, city = city, min_price = int(min_price), max_price = int(max_price))
        craigslist_search.times_called = craigslist_search.times_called + 1
        craigslist_search.save()
        
        ebay_search = Ebay_Search.objects.get(keyword = keyword, min_price = int(min_price), max_price = int(max_price))
        ebay_search.times_called = ebay_search.times_called + 1
        ebay_search.save()
        
    except (Craigslist_Search.MultipleObjectsReturned, Ebay_Search.MultipleObjectsReturned, Craigslist_Search.DoesNotExist, Ebay_Search.DoesNotExist) as e:
        print 'Cache Miss: Scrapping'
        aggregator.scrape_data(keyword,max_price,min_price,city)
        artifical_timeout = 0
        while True:
            try:
                print 'Waiting for scrape-results'
                ebay_search       = Ebay_Search.objects.get(keyword = str(keyword), min_price = int(min_price), max_price = int(max_price))
                craigslist_search = Craigslist_Search.objects.get(keyword = str(keyword), city = city, min_price = int(min_price), max_price = int(max_price))
                break
            except (Ebay_Search.DoesNotExist, Craigslist_Search.DoesNotExist) as e:
                if(artifical_timeout == 30):
                    timed_out = True
                    break
                else:
                    time.sleep(.5)
                    artifical_timeout = artifical_timeout + .5

    if(timed_out == False):
        try:
            tmp_user = Users.objects.get(user_id = key)
            print 'Found User'

            if craigslist_search not in tmp_user.craigslist_search:
                tmp_user.craigslist_search.insert(0,craigslist_search)
                print "Added Craigslist_Search to: " + tmp_user.email
            else:
                tmp_user.craigslist_search.insert(0, tmp_user.craigslist_search.pop(tmp_user.craigslist_search.index(craigslist_search)))
                print "Search already in list! Moved to front"

            if ebay_search not in tmp_user.ebay_search:
                tmp_user.ebay_search.insert(0,ebay_search)
                print "Added Ebay_Search to: " + tmp_user.email
            else:
                tmp_user.ebay_search.insert(0, tmp_user.ebay_search.pop(tmp_user.ebay_search.index(ebay_search)))
                print "Search already in list! Moved to front"
            tmp_user.save()
                
        except Users.DoesNotExist:
            return render(request, 'project/dashboard.html')

        results = get_results(craigslist_search)
        return render(request, 'project/dashboard.html', {'user_searches':tmp_user.craigslist_search,'result_list':results})
        
    else:
        return render(request, 'project/dashboard.html', {'message':'No results found!'})

def get_results(craigslist_search):
    keyword = craigslist_search.keyword
    min_price = craigslist_search.min_price
    max_price = craigslist_search.max_price
    
    results = {}
    results1 = []
    
    c_count = 0
    e_count = 0
    
    for c_item in Craigslist_Item.objects.all().filter(keyword = keyword, city__in = craigslist_search.near_cities, price__range = (int(min_price), int(max_price))).order_by('-time_created'):
        results1.append((c_count,c_item.title,'http://'+c_item.url,'$'+str(c_item.price),c_item.time_created.strftime('%Y-%m-%d %H:%M'),'Craigslist'))
        c_count = c_count + 1
    
    e_count = c_count

    for e_item in Ebay_Item.objects.all().filter(keyword = keyword, price__range = (int(min_price), int(max_price))).order_by('-time_created'):
        results1.append((e_count,e_item.title, e_item.url,'$'+str(e_item.price),e_item.time_created.strftime('%Y-%m-%d %H:%M'),'eBay'))
        e_count = e_count + 1

    results_list = sorted(results1, key=lambda tup: tup[4], reverse=True)

    count = 0
    
    for result in results_list:
        results[count] = {'title':result[1], 'url':result[2], 'price':result[3], 'time':result[4], 'type':result[5]}
        count = count + 1

    dict1 = collections.OrderedDict(sorted(results.items()))
    
    print json.dumps(dict1, default=json_util.default, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
    
    return dict1

'''
|||||||||||||||||||| monitordash.html ||||||||||||||||||||
        Call data_analysis when hit submit
        Will then query the database and return results
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||
'''
def monitordash(request):
    return render(request, 'project/monitordash.html')

def data_analysis(request):
    if request.GET['filter'] == "popular":
        results = {}
        results1 = []
            
        c_count = 0
        
        for c_item in Craigslist_Search.objects.order_by('-times_called')[:10]:
            results1.append((c_count,c_item.times_called,c_item.keyword,c_item.city,'$'+str(c_item.min_price),'$'+str(c_item.max_price)))
            c_count = c_count + 1

        results_list = sorted(results1, key=lambda tup: tup[1], reverse=True)

        count = 0
        
        for result in results_list:
            results[count] = {'times_called':result[1], 'keyword':result[2], 'city':result[3], 'min_price':result[4], 'max_price':result[5]}
            count = count + 1

        dict1 = collections.OrderedDict(sorted(results.items()))

        print json.dumps(dict1, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
        return render(request,'project/monitordash.html',{'message':'Most Popular Searches',"results":dict1})

    if request.GET['filter'] == "price":
        results = {}
        results1 = []
        
        c_count = 0
        
        for c_item in Craigslist_Item.objects.order_by('-price')[:10]:
            results1.append((c_count,c_item.title,'http://'+c_item.url,c_item.price,c_item.time_created.strftime('%Y-%m-%d %H:%M'),'Craigslist'))
            c_count = c_count + 1
        
        e_count = c_count + 1
        
        for e_item in Ebay_Item.objects.order_by('-price')[:10]:
            results1.append((e_count,e_item.title, e_item.url,e_item.price,e_item.time_created.strftime('%Y-%m-%d %H:%M'),'eBay'))
            e__count = e_count + 1

        results_list = sorted(results1, key=lambda tup: tup[3], reverse=True)

        count = 0
            
        for result in results_list[:10]:
            results[count] = {'title':result[1], 'url':result[2], 'price':result[3], 'time':result[4], 'type':result[5]}
            count = count + 1

        dict1 = collections.OrderedDict(sorted(results.items()))

        print json.dumps(dict1, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
        return render(request,'project/monitordash.html',{'message':'Most Expensive Searches',"results":dict1})

    if request.GET['filter'] == "queue":
        results = {}
        results1 = []

        q_count = 0
        
        for q_item in Job_Queue.objects.all():
            results1.append((q_count,q_item.keyword,q_item.city,q_item.max_price,q_item.min_price))
            q_count = q_count + 1

        results_list = sorted(results1, key=lambda tup: tup[0])
    
        count = 0
        
        for result in results_list:
            results[count] = {'keyword':result[1], 'city':result[2], 'max_price':result[3], 'min_price':result[4]}
            count = count + 1

        dict1 = collections.OrderedDict(sorted(results.items()))
        
        print json.dumps(dict1, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
        return render(request,'project/monitordash.html',{'message':'Job Queue',"results":dict1})

    return render(request, 'project/monitordash.html')


'''
|||||||||||||||||||| Helper Fuctions ||||||||||||||||||||
    Helper Functions that update results
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||
'''
def update_current_items(request):
    request_list = request.GET['searchlist'].split('+')
    keyword   = str(request_list[0])
    city      = str(request_list[1])
    min_price = int(request_list[2])
    max_price = int(request_list[3])
    
    if request.COOKIES.has_key('id'):
        user_id = request.COOKIES['id']
    else:
        user_id = 'None'

    craigslist_search = Craigslist_Search.objects.get(keyword = keyword, city = city, min_price = min_price, max_price = max_price)
    ebay_search = Ebay_Search.objects.get(keyword = keyword, min_price = min_price, max_price = max_price)

    results = get_updated_results(craigslist_search, ebay_search, user_id)

    return render(request, 'project/dashboard.html', {'user_searches':Users.objects.get(user_id = user_id).craigslist_search, 'result_list':results})

def get_updated_results(craigslist_search, ebay_search, user_id):
    try:
        tmp_user = Users.objects.get(user_id = user_id)
        print 'Found User'
        if craigslist_search not in tmp_user.craigslist_search:
            tmp_user.craigslist_search.insert(0,craigslist_search)
            print "Added Craigslist_Search to: " + tmp_user.email
        else:
            tmp_user.craigslist_search.insert(0, tmp_user.craigslist_search.pop(tmp_user.craigslist_search.index(craigslist_search)))
            print "Search already in list! Moved to front"

        if ebay_search not in tmp_user.ebay_search:
            tmp_user.ebay_search.insert(0,ebay_search)
            print "Added Ebay_Search to: " + tmp_user.email
        else:
            tmp_user.ebay_search.insert(0, tmp_user.ebay_search.pop(tmp_user.ebay_search.index(ebay_search)))
            print "Search already in list! Moved to front"
        tmp_user.save()
    except Users.DoesNotExist:
        print 'User Doesnt Exist'

    return get_results(craigslist_search)
