import ebaysdk
from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError

import json

def fetch_results(item):
    try:
        api = Finding(appid="Jeremiah-c9e4-41cd-93a3-db5086f58faf")
        response = api.execute('findItemsAdvanced', {'keywords': item})
#        print json.dumps(response.dict(), sort_keys=True, indent=4, separators=(',', ': '))

    except ConnectionError as e:
        print(e)
        print(e.response.dict())

def ebay_scrape(item):
    fetch_results(item)