import ebaysdk
import json
import re
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

from project.models import *
from ebaysdk.exception import ConnectionError
from ebaysdk.finding import Connection as Finding
from django.utils import timezone

def fetch_results(user,item,min_price,max_price):
    try:
        api = Finding(appid="Jeremiah-c9e4-41cd-93a3-db5086f58faf")
        response = api.execute('findItemsAdvanced', {'keywords': item, 'sortOrder': 'StartTimeNewest', 'itemFilter': {'name' : 'MinPrice' , 'value' : min_price, 'paramName' : 'Currency', 'paramValue' :'USD'}, 'itemFilter': {'name' : 'MaxPrice' , 'value' : max_price, 'paramName' : 'Currency', 'paramValue' :'USD'}})

        dictionary = response.dict()

        if 'item' in dictionary['searchResult']:
            count = 1
            temp_dictionary = {}
            
            for key in dictionary['searchResult']['item']:
                    item_id = key['itemId']
                    title   = key['title']
                    url     = key['viewItemURL']
                    price   = key['sellingStatus']['currentPrice']['value']

                    temp_dictionary[str(count)] = {'title': title.strip(), 'url': url.strip(), 'price' : price.strip(), 'key': item_id.strip()};
                    count = count + 1
                   
            #print json.dumps(temp_dictionary, sort_keys=True, indent=4, separators=(',', ': '))
        
            send_to_database(user,item,min_price,max_price,temp_dictionary)
        else:
            count = 0

        return count
    except ConnectionError as e:
        print(e)
        print(e.response.dict())
        return 0 

def send_to_database(user_keyword,item_keyword,min_price_keyword,max_price_keyword,dict):

    min_price_keyword  = int(min_price_keyword)
    max_price_keyword  = int(max_price_keyword)

    for item_key in dict:
        try:
            i = Ebay_Item.objects.get(key = dict[item_key]['key'])
        except Ebay_Item.DoesNotExist:
            i = Ebay_Item.objects.create(title = dict[item_key]['title'], keyword = item_keyword, url = dict[item_key]['url'], price = int(float(dict[item_key]['price'])), key = dict[item_key]['key'],time_created = timezone.now())
            i.save()

# /////////// NEED CURRENT USER -> THEN CHECK IF THEY ALRADY SEARCHED      ///////////
# //////////  IF THEY HAVEN'T SEARCHED, THEN ADD CRAIGSLIST SEARCH TO USER ///////////
#    if(len(items_list) > 0):
#        try:
#            s = Ebay_Search.objects.get(keyword = item_keyword, min_price = min_price_keyword, max_price = max_price_keyword)
#            s.items.extend(items_list)
#        except Ebay_Search.DoesNotExist:
#            s = Ebay_Search.objects.create(keyword = item_keyword, min_price = min_price_keyword, max_price = max_price_keyword, items = items_list)
#        s.save()
#        print 'Inserted Ebay Search!'
# /////////// NEED CURRENT USER -> THEN CHECK IF THEY ALRADY SEARCHED      ///////////
# //////////  IF THEY HAVEN'T SEARCHED, THEN ADD CRAIGSLIST SEARCH TO USER ///////////

    #STILL HAVE TO DO USER

def ebay_scrape(user,item,min_price,max_price):
    return fetch_results(user,item,min_price,max_price)
