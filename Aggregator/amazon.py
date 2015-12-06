import bottlenose
import xmltodict
import lxml
import json
    
def main():
    amazon = bottlenose.Amazon('AKIAIYZI6XMXPN2RSYCQ', 'VdAocVvKYX3c1LyI4kTaJGLjYeweWy5pUdkSONAV', 'largescalepro-20')
    response = amazon.ItemSearch(Keywords="xbox", SearchIndex="All", ItemPage="5")

    print json.dumps(xmltodict.parse(response), sort_keys=True, indent=4, separators=(',', ': '))



main()