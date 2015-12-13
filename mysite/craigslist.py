import sys
import feedparser
import requests
import threading
import json
import re
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

from lxml import html
from project.models import *
from django.utils import timezone

def fetch_results(keyword,city,min_price,max_price):
    xml = feedparser.parse('http://'+city+'/search/sss?format=rss?&min_price='+min_price+'&max_price='+max_price+'&query='+keyword.replace(' ','%20')+'&sort=rel')
    dict = {}
    index = 0
 
    for post in xml.entries:
        entry = post.title.replace('&#x0024;','$') + ": " + post.link + "\n"
        
        tmp = entry.split('http://')

        title = tmp[0].replace(':','')
        url   = tmp[1]

        price = "0"
        
        if '$' in title:
            split_title = title.split(' ')
            for x in range(len(split_title)-1):
                if '$' in split_title[x]:
                    price = re.sub("[^0-9]", "", split_title[x].replace('$',' '))
		    if not price:
                        price = "0"
                    break
        
        for letters in tmp[1].split('/'):
            if '.html' in letters:
                key = letters.replace('.html','')

        dict[str(index)] = {'title': title.strip(), 'url': url.strip(), 'price' : price.strip(), 'key': key.strip()};
        index = index + 1
	
    return dict

def get_nearby_cities(city):
    #Hardcoding for now - TODO
    url = city

    page = requests.get('http://'+url)
    tree = html.fromstring(page.text)
    
    cities = [url]
    
    for link in tree.xpath('//*[@id="rightbar"]/ul/li[1]/ul//a'):
        cities.append(link.attrib['href'].replace('//','').replace('/',''))

    return cities

def craigslist_scrape(user,city,keyword_item,min_price,max_price):
    dict = {}
    cities = get_nearby_cities(city)
    num_of_items = 0
        
    for x in range(len(cities)):
        tmp_dict = fetch_results(keyword_item,cities[x],min_price,max_price)
        num_of_items = num_of_items + len(tmp_dict)
        dict[str(cities[x])] = tmp_dict

    min_price = int(min_price)
    max_price = int(max_price)

    num_cached = 0
    num_added  = 0 

    num_searches_cached = 0
    num_searches_added  = 0

    for city_key in dict:
        for item_key in dict[city_key]:
            try:
                i = Craigslist_Item.objects.get(key = dict[city_key][item_key]['key'])
                num_cached = num_cached + 1
            except Craigslist_Item.DoesNotExist:
                i = Craigslist_Item.objects.create(title = dict[city_key][item_key]['title'], keyword = keyword_item, url = dict[city_key][item_key]['url'], price = int(float(dict[city_key][item_key]['price'])), key = dict[city_key][item_key]['key'], city = city_key,time_created = timezone.now())
                num_added = num_added + 1
                i.insert_one()
        try:
            c_search = Craigslist_Search.objects.get(keyword = keyword_item, city = city_key, min_price = min_price, max_price = max_price)
            num_searches_cached = num_searches_cached + 1
        except Craigslist_Search.DoesNotExist:
            c_search = Craigslist_Search.objects.create(keyword = keyword_item, city = city_key, near_cities = cities, min_price = min_price, max_price = max_price)
            num_searches_added = num_searches_added + 1


    print "Craigslist_Item num_cached: " + str(num_cached) + " num_added: " + str(num_added)
    print "Craigslist_Search num_cached: " + str(num_searches_cached) + " num_added: " + str(num_searches_added)

# /////////// NEED CURRENT USER -> THEN CHECK IF THEY ALRADY SEARCHED      ///////////
# //////////  IF THEY HAVEN'T SEARCHED, THEN ADD CRAIGSLIST SEARCH TO USER ///////////
#        if(len(items_list) > 0):
#            try:
#                s = Craigslist_Search.objects.get(keyword = keyword_item, city = city_key, min_price = min_price, max_price = max_price)
#                s.items.extend(items_list)
#            except Craigslist_Search.DoesNotExist:
#                s = Craigslist_Search.objects.create(keyword = keyword_item, city = city_key, near_cities = cities, min_price = min_price, max_price = max_price, items = items_list)
#            s.save()
#            print 'Inserted Craigslist Search!'
# /////////// NEED CURRENT USER -> THEN CHECK IF THEY ALRADY SEARCHED      ///////////
# //////////  IF THEY HAVEN'T SEARCHED, THEN ADD CRAIGSLIST SEARCH TO USER ///////////

#    print json.dumps(dict, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))

    return num_of_items
