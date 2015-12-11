import ebaysdk
import demjson
import json
import re

from pymongo import MongoClient
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

            jsond = demjson.encode(temp_dictionary)
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
    client = MongoClient('localhost', 27017)
    db = client.largescale

    items_list = []
    for item_key in dict:
        item = {'title' : dict[item_key]['title'], 'url' : dict[item_key]['url'], 'price' : dict[item_key]['price'], 'key' : dict[item_key]['key']}
        db_item = db.Item.insert_one(item).inserted_id
        items_list.append(db_item)
    
    if(len(items_list) > 0):
        search = {'keyword' : item_keyword, 'min_price' : min_price_keyword, 'max_price' : max_price_keyword, 'items' : items_list}
        db_search = db.Ebay_Search.insert_one(search).inserted_id
        print 'Inserted Ebay Search!'

def ebay_scrape(user,item,min_price,max_price):
    return fetch_results(user,item,min_price,max_price)
