import bottlenose
import xmltodict
import lxml
import json
    
def fetch_results(item):
    amazon = bottlenose.Amazon('AKIAIYZI6XMXPN2RSYCQ', 'VdAocVvKYX3c1LyI4kTaJGLjYeweWy5pUdkSONAV', 'largescalepro-20')
    response = amazon.ItemSearch(Keywords=item, SearchIndex="All", ItemPage="5")

#    print json.dumps(xmltodict.parse(response), sort_keys=True, indent=4, separators=(',', ': '))

def amazon_scrape(item):
    fetch_results(item)