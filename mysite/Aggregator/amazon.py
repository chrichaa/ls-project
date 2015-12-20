import bottlenose
import xmltodict
import lxml
import json
    
def fetch_results(user,item,min_price,max_price):
    amazon = bottlenose.Amazon('', '', '')
    response = amazon.ItemSearch(Title=item, MaximumPrice = max_price+'00', MinimumPrice = min_price+'00', SearchIndex="Electronics", ItemPage="5")
    
    print json.dumps(xmltodict.parse(response), sort_keys=True, indent=4, separators=(',', ': '))

    dictionary = xmltodict.parse(response)
    
    if 'Item' in dictionary:
        count = 1

        temp_dictionary = {}

        for key in dictionary['ItemSearchResponse']['Items']['Item']:
            item_id = key['ASIN']
            title   = key['ItemAttributes']['Title']
            url     = key['DetailPageURL']

            temp_dictionary[str(count)] = {'Title' : title.strip(), 'Url' : url.strip(), 'Key' : item_id.strip()}
            count = count + 1

        jsond = demjson.encode(temp_dictionary)
        print json.dumps(xmltodict.parse(response), sort_keys=True, indent=4, separators=(',', ': '))
    else:
        count = 0

#TODO - CONNECT TO MONGO

    return count

def amazon_scrape(user,item,min_price,max_price):
    return fetch_results(user,item,min_price,max_price)
