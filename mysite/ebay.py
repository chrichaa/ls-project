import ebaysdk
import json
import re
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

from project.models import Users,Ebay_Search,Item
from decimal import *
from ebaysdk.exception import ConnectionError
from ebaysdk.finding import Connection as Finding

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
    items_list = []
    min_price_keyword  = "{:.2f}".format(float(min_price_keyword))
    max_price_keyword  = "{:.2f}".format(float(max_price_keyword))

    for item_key in dict:
        i = Item.objects.create(title = dict[item_key]['title'], url = dict[item_key]['url'], price = "{:.2f}".format(float(dict[item_key]['price'])), key = dict[item_key]['key'])
        i.save()
        items_list.append(i)
    
    if(len(items_list) > 0):
        s = Ebay_Search.objects.create(keyword = item_keyword, min_price = min_price_keyword, max_price = max_price_keyword, items = items_list)
        s.save()
        print 'Inserted Ebay Search!'

    #STILL HAVE TO DO USER

def ebay_scrape(user,item,min_price,max_price):
    return fetch_results(user,item,min_price,max_price)
