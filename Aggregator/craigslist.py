import sys
import feedparser
import requests
import threading
import demjson
import json
import re

from pymongo import MongoClient
from lxml import html

def fetch_results(keyword,city,min_price,max_price):
    xml = feedparser.parse('http://'+city+'/search/sss?format=rss?&min_price='+min_price+'&max_price='+max_price+'&query='+keyword.replace(' ','%20')+'&sort=rel')
    dict = {}
    index = 0

    for post in xml.entries:
        entry = post.title.replace('&#x0024;','$') + ": " + post.link + "\n"
        
        tmp = entry.split('http://')

        title = tmp[0].replace(':','')
        url   = tmp[1]

        price = None
        
        if '$' in title:
            split_title = title.split(' ')
            for x in range(len(split_title)-1):
                if '$' in split_title[x]:
                    price = re.sub("[^0-9]", "", split_title[x].replace('$',' '))
		    break
        
        for letters in tmp[1].split('/'):
            if '.html' in letters:
                key = letters.replace('.html','')

        dict[str(index)] = {'title': title.strip(), 'url': url.strip(), 'price' : price, 'key': key.strip()};
        index = index + 1

    return dict

def get_nearby_cities(city):
    #Hardcoding for now - TODO
    url = city+'.craigslist.org'

    page = requests.get('http://'+url)
    tree = html.fromstring(page.text)
    
    cities = [url]
    
    for link in tree.xpath('//*[@id="rightbar"]/ul/li[1]/ul//a'):
        cities.append(link.attrib['href'].replace('//','').replace('/',''))

    return cities

def craigslist_scrape(user,city,keyword_item,min_price,max_price):
    client = MongoClient('localhost', 27017)
    db = client.largescale

    dict = {}
    cities = get_nearby_cities(city)
    
    num_of_items = 0
        
    for x in range(len(cities)):
        tmp_dict = fetch_results(keyword_item,cities[x],min_price,max_price)
        num_of_items = num_of_items + len(tmp_dict)
        dict[str(cities[x])] = tmp_dict

    jsonD = demjson.encode(dict)

    items_list = []
    for city_key in dict:
        for item_key in dict[city_key]:
            item = {'title' : dict[city_key][item_key]['title'], 'url' : dict[city_key][item_key]['url'], 'price' : dict[city_key][item_key]['price'], 'key' : dict[city_key][item_key]['key']}
            db_item = db.Item.insert_one(item).inserted_id
            items_list.append(db_item)
        
        if(len(items_list) > 0):
            search = {'keyword' : keyword_item, 'city' : city_key, 'min_price' : min_price, 'max_price' : max_price, 'items' : items_list}
            db_search = db.Craigslist_Search.insert_one(search).inserted_id
            print 'Inserted Craigslist Search!'
        items_list = []
            
#    print json.dumps(dict, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))

    return num_of_items

    #Send results to database - TODO

#    print 'Found '+str(len(feed))+' results'
#    counter = 1
#    for entry in feed:
#        print str(counter) + ': ' + entry
#        counter = counter + 1
