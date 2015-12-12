import sys
import socket
import json

import craigslist
import ebay
#import amazon

import threading
import time
import inspect

from sys import argv

job_queue = []
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
            if(len(job_queue) > 0):
                if((job_queue[0]['timestamp'] == 0) or (((int(time.time()) - int(job_queue[0]['timestamp']))/60) >= 15)):
                    print job_queue
                    tmp = job_queue.pop(0)

                    start_scraping(conn,tmp)

                    tmp['timestamp'] = int(time.time())
                    job_queue.append(tmp)

def start_scraping(conn,data):
    print 'Scraping: '+ data['keyword'] + ' From: ' + data['city'] + ' For: ' + data['user'] + ' Between $' + data['min_price'] + ' and $' + data['max_price']
    #locationFile.write(data['city'])
    begin = time.time()
    
    print "Scrapping Craigslist ...."
    num_of_craigslist_results = craigslist.craigslist_scrape(data['user'],data['city'],data['keyword'],data['min_price'],data['max_price'])
    print ("Craigslist Results: %d")%(num_of_craigslist_results)
#    #resultFile.write( integer with number of results)

# ///////////////// WARNING - AMAZON DOESNT WORK, DO NOT USE /////////////////
#    print "Scrapping Amazon ...."
#    num_of_amazon_results = amazon.amazon_scrape(data['user'],data['keyword'],data['min_price'],data['max_price'])
#    print ("Amazon Results: %d")%(num_of_amazon_results)
#    resultFile.write( integer with number of results)
# ///////////////// WARNING - AMAZON DOESNT WORK, DO NOT USE /////////////////

    print "Scrapping eBay ...."
    num_of_ebay_results = ebay.ebay_scrape(data['user'],data['keyword'],data['min_price'],data['max_price'])
    print ("eBay Results: %d")%(num_of_ebay_results)
#    #resultFile.write( integer with number of results)

    print ('Done! Took: %d Seconds')%(int(time.time()-begin))
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
                job_queue.insert(0,parsed_json)
                reply = 'Added '+data+' to priority queue'

        conn[0].sendall(reply)

    conn[0].close()

def serve():
    print 'Running Server ....'

    s = socket.socket()
    host = socket.gethostname()
    port = 12348
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
