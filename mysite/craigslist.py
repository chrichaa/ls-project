import sys
import feedparser
import requests
import threading
import json
import re
import os
from threading import Thread

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

import project.cities_dictionary as cities_dictionary

from bson import json_util
from Queue import Queue
from lxml import html
from project.models import *
from django.utils import timezone
from time import mktime
from datetime import datetime

def fetch_results(keyword,city,min_price,max_price,q):
    xml = feedparser.parse('http://'+city+'/search/sss?format=rss?&min_price='+min_price+'&max_price='+max_price+'&query='+keyword.replace(' ','%20')+'&sort=rel')
    dict = {}
    index = 0
    
    for post in xml.entries:
        entry = post.title.replace('&#x0024;','$') + ": " + post.link + "\n"
        time  = datetime.fromtimestamp(mktime(post.published_parsed))
        tmp = entry.split('http://')

        title = tmp[0].replace(':','')
        url   = tmp[1]

        price = "0"
        
        if '$' in title:
            split_title = title.split(' ')
            for x in range(len(split_title)-1, -1, -1):
                if '$' in split_title[x]:
                    price = re.sub("[^0-9]", "", split_title[x].replace('$',' '))
                    split_title.remove(split_title[x])
                    title = ' '.join(split_title)
		    if not price:
                        price = "0"
                    break
        
        for letters in tmp[1].split('/'):
            if '.html' in letters:
                key = letters.replace('.html','')

        dict[str(index)] = {'title': title.strip(), 'url': url.strip(), 'price' : price.strip(), 'time' : time, 'key': key.strip()};
        index = index + 1
	
    q.put((city,dict))
    q.task_done()

def get_nearby_cities(city):
    return cities_dictionary.get_close_cities()[city]

def craigslist_scrape(city,keyword_item,min_price,max_price):
    dict = {}
    cities = get_nearby_cities(city)
    num_of_items = 0

    min_price = int(min_price)
    max_price = int(max_price)

    num_cached = 0
    num_added  = 0

    num_searches_cached = 0
    num_searches_added  = 0
    
    q = Queue()
    threads = []

    for x in range(len(cities)):
        try:
            Craigslist_Search.objects.get(keyword = keyword_item, city = str(cities[x]), min_price = min_price, max_price = max_price)
            t = Thread(target=fetch_results, args=(keyword_item,cities[x],str(min_price),str(max_price),q))
            t.start()
            threads.append(t)
        
        except Craigslist_Search.DoesNotExist:
            try:
                Craigslist_Search.objects.get(keyword = keyword_item, city = str(cities[x]), min_price__lte = min_price, max_price__gte = max_price)
                num_searches_cached = num_searches_cached + 1
               
                q.put((city,{}))
                q.task_done()

            except Craigslist_Search.MultipleObjectsReturned:
                q.put((city,{}))
                q.task_done()

            except Craigslist_Search.DoesNotExist:
                t = Thread(target=fetch_results, args=(keyword_item,cities[x],str(min_price),str(max_price),q))
                t.start()
                threads.append(t)
                       
    for t in threads:
        t.join()
                       
    for object in iter(q.get, None):
       if q.empty():
           break 
       if not object[1]:
            dict[str(object[0])] = {}
       else:
            dict[str(object[0])] = object[1]
            num_of_items = num_of_items + len(object[1])
                           
    for city_key in dict:
        for item_key in dict[city_key]:
            try:
                i = Craigslist_Item.objects.get(key = dict[city_key][item_key]['key'])
                num_cached = num_cached + 1
            
            except Craigslist_Item.DoesNotExist:
                i = Craigslist_Item.objects.create(title = dict[city_key][item_key]['title'], keyword = keyword_item, url = dict[city_key][item_key]['url'], price = int(float(dict[city_key][item_key]['price'])), key = dict[city_key][item_key]['key'], city = city_key,time_created = dict[city_key][item_key]['time'])
                num_added = num_added + 1
    
        try:
            c_search = Craigslist_Search.objects.get(keyword = keyword_item, city = city_key, min_price = min_price, max_price = max_price)
            num_searches_cached = num_searches_cached + 1
            if num_added >= 1:
                c_search.result_amount = c_search.result_amount + num_added
        
        except Craigslist_Search.DoesNotExist:
            c_search = Craigslist_Search.objects.create(keyword = keyword_item, city = city_key, near_cities = cities, min_price = min_price, max_price = max_price, result_amount = num_of_items, times_called = 1)
            num_searches_added = num_searches_added + 1

        c_search.save()

    print "Craigslist_Item num_cached: " + str(num_cached) + " num_added: " + str(num_added)
    print "Craigslist_Search num_cached: " + str(num_searches_cached) + " num_added: " + str(num_searches_added)

#    print json.dumps(dict, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))

    return num_of_items
