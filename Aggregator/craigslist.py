import sys
import feedparser
import requests
import threading
import demjson
from lxml import html

def fetch_results(keyword,city):
    xml = feedparser.parse('http://'+city+'/search/sss?format=rss&query='+keyword+'&sort=rel')
    dict = {}
    index = 0

    for post in xml.entries:
        entry = post.title.replace('&#x0024;','$') + ": " + post.link + "\n"
        
        tmp = entry.split('http://')

        title = tmp[0].replace(':','')
        url   = tmp[1]
        key   = tmp[1].split('/')[3].replace('.html','')
        
        print title + ' ' + url + ' ' + key

        dict[str(index)] = {'Title': title, 'Url': url, 'Key': key};
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

def craigslist_scrape(city,item):
    dict = {}
    cities = get_nearby_cities(city)
    
    print cities
    
    for x in range(len(cities)):
        tmp_dict = fetch_results(item,cities[x])
        dict[str(cities[x])] = tmp_dict

    json = demjson.encode(dict)
    #Send results to database - TODO




#    print 'Found '+str(len(feed))+' results'
#    counter = 1
#    for entry in feed:
#        print str(counter) + ': ' + entry
#        counter = counter + 1