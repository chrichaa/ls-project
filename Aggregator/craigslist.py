import sys
import feedparser
import requests
import threading
from lxml import html

class myThread (threading.Thread):
    def __init__(self, threadID, keyword, city, feed):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.keyword = keyword
        self.city = city
        self.feed = feed
    
    def run(self):
        threadLock.acquire()
        fetch_results(self.keyword,self.city,self.feed)
        threadLock.release()

threadLock = threading.Lock()
threads = []

def fetch_results(keyword,city,tmp_feed):
    xml = feedparser.parse('http://'+city+'/search/sss?format=rss&query='+keyword+'&sort=rel')

    for post in xml.entries:
        entry = post.title.replace('&#x0024;','$') + ": " + post.link + "\n"
        tmp_feed.append(entry)

    #Send results to database - TODO

def get_nearby_cities(city):
    #Hardcoding for now - TODO
    url = city+'.craigslist.org'

    page = requests.get('http://'+url)
    tree = html.fromstring(page.text)
    
    cities = [url]

    for link in tree.xpath('//*[@id="rightbar"]/ul/li[1]/ul//a'):
        cities.append(link.attrib['href'].replace('//',''))

    return cities

def craigslist_scrape(city,item):
    
    cities = get_nearby_cities(city)
    feed = []
    
    tmp_threads = []
    
    for x in range(len(cities)):
        thread = myThread(x, item, cities[x], feed)
        tmp_threads.append(thread)
    
    for thread in tmp_threads:
        thread.start()

    for thread in tmp_threads:
        threads.append(thread)

    print 'Fetching Craigslist'
    for t in threads:
        sys.stdout.write(".")
        sys.stdout.flush()
        t.join()

    print "Exiting Main Thread"

    print 'Found '+str(len(feed))+' results'
#    counter = 1
#    for entry in feed:
#        print str(counter) + ': ' + entry
#        counter = counter + 1