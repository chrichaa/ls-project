import sys
import socket
import json

import craigslist
import ebay
#import amazon

import threading
import time
import inspect
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

from project.models import *
from django.utils import timezone
from sys import argv

#job_queue = []
conn = None

lock = threading.Lock()

class Thread(threading.Thread):
    def __init__(self, t, *args):
        threading.Thread.__init__(self, target=t, args=args)
        self.start()

def check_queue():
    while True:
        caller = inspect.getouterframes(inspect.currentframe())[1][3]
        with lock:
            if(Job_Queue.objects.exists()):
                first_in_queue = Job_Queue.objects.order_by('time_created').first()
                if((first_in_queue.time_created == 0) or (((int(time.time()) - int(first_in_queue.time_created))/60) >= 15)):
                    #print job_queue
                    #tmp = job_queue.pop(0)

                    tmp = first_in_queue
                    start_scraping(conn,tmp)
                    first_in_queue.delete()

                    Job_Queue.objects.create(keyword = tmp.keyword, max_price = int(tmp.max_price), min_price = int(tmp.min_price), city = tmp.city, time_created = int(time.time()))

                    #tmp['timestamp'] = int(time.time())
                    #job_queue.append(tmp)

def start_scraping(conn,data):
    print 'Scraping: '+ data.keyword + ' From: ' + data.city + ' Between $' + str(data.min_price) + ' and $' + str(data.max_price)
    #locationFile.write(data['city'])
    begin = time.time()
    
    print "Scrapping Craigslist ...."
    num_of_craigslist_results = craigslist.craigslist_scrape(data.city,data.keyword,data.min_price,data.max_price)
    print ("Craigslist Results: %d")%(num_of_craigslist_results)
#    #resultFile.write( integer with number of results)

# ///////////////// WARNING - AMAZON DOESNT WORK, DO NOT USE /////////////////
#    print "Scrapping Amazon ...."
#    num_of_amazon_results = amazon.amazon_scrape(data['keyword'],data['min_price'],data['max_price'])
#    print ("Amazon Results: %d")%(num_of_amazon_results)
#    resultFile.write( integer with number of results)
# ///////////////// WARNING - AMAZON DOESNT WORK, DO NOT USE /////////////////

    print "Scrapping eBay ...."
    num_of_ebay_results = ebay.ebay_scrape(data.keyword,data.min_price,data.max_price)
    print ("eBay Results: %d")%(num_of_ebay_results)
#    #resultFile.write( integer with number of results)

    print ('Done! Took: %d Seconds')%(int(time.time()-begin))
    print ('-----------------------------------------------')
    print (' \n')
#    #timeFile.write('Done! Took: %d Seconds')%(int(time.time()-begin))
#    #remove formatting for analysis

def add_to_queue(conn):
    while True:
        data = conn[0].recv(1024)
        
        if not data:
            reply = 'Did not add to priority queue'
            break
        else:
            parsed_json = json.loads(data)
            
            caller = inspect.getouterframes(inspect.currentframe())[1][3]
            print "Inside %s()" % caller
            
            with lock:
                print "Acquiring lock"
                Job_Queue.objects.create(keyword = parsed_json['keyword'], max_price = int(parsed_json['max_price']), min_price = int(parsed_json['min_price']), city = parsed_json['city'], time_created = 0)
#                job_queue.insert(0,parsed_json)
                reply = 'Added '+data+' to priority queue'

        conn[0].sendall(reply)

    conn[0].close()

def serve():
    print 'Running Server ....'

    s = socket.socket()
    host = socket.gethostname()
    port = 12350
    s.bind((host, port))

    job_queue = []

    s.listen(10)

    while 1:
        print 'Socket is listening ....'
        try:
            conn, addr = s.accept()
            print 'Connected with ' + addr[0] + ':' + str(addr[1])
            
            Thread(add_to_queue ,(conn,))
        
        except (KeyboardInterrupt, SystemExit):
            s.close()
            sys.exit()

    s.close()

if __name__ == '__main__':
    #timeFile = open(timestat.txt, 'w')
    #locationFile = open(locationstat.txt, 'w')
    #keywordFile= open(keywordFile.txt, 'w')
    #resultFile= open(resultFile.txt, 'w')
    Thread(check_queue)
    Thread(serve)
