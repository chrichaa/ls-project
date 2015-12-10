import ebaysdk
from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError
import demjson
import json

def fetch_results(user,item,min_price,max_price):
    try:
        api = Finding(appid="Jeremiah-c9e4-41cd-93a3-db5086f58faf")
        response = api.execute('findItemsAdvanced', {'keywords': item, 'sortOrder': 'StartTimeNewest', 'itemFilter': {'name' : 'MinPrice' , 'value' : min_price, 'paramName' : 'Currency', 'paramValue' :'USD'}, 'itemFilter': {'name' : 'MaxPrice' , 'value' : max_price, 'paramName' : 'Currency', 'paramValue' :'USD'}})

        dictionary = response.dict()

        if 'item' in dictionary:
            count = 1
            temp_dictionary = {}
            
            for key in dictionary['searchResult']['item']:
                    item_id = key['itemId']
                    title   = key['title']
                    url     =  key['viewItemURL']

                    temp_dictionary[str(count)] = {'Title' : title.strip(), 'Url' : url.strip(), 'Key' : item_id.strip()}
                    count = count + 1

            jsond = demjson.encode(temp_dictionary)
    #        print json.dumps(temp_dictionary, sort_keys=True, indent=4, separators=(',', ': '))
        else:
            count = 0

        return count
    except ConnectionError as e:
        print(e)
        print(e.response.dict())

def ebay_scrape(user,item,min_price,max_price):
    return fetch_results(user,item,min_price,max_price)