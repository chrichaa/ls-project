import sys
import socket
import json

import craigslist
import ebay

from thread import *

from Queue import Queue
from heapq import heappush, heappop


def check_queue():
    while True:
        if((len(test) > 0) and (test[0][1] == 0)):
            print test
            test[0] = (test[0][0],15)
            start_scraping(conn,test[0][0])

            #Still have to handle queue - TODO

s = socket.socket()
host = socket.gethostname()
port = 12345
s.bind((host, port))

test = []

start_new_thread(check_queue ,())

s.listen(10)                
print 'Socket is listening'

def add_to_queue(conn):
    while True:
        
        #Receiving from client
        data = conn.recv(1024)
        
        if not data:
            reply = 'Did not add to priority queue'
            break
        else:
            parsed_json = json.loads(data)
            test.insert(0,(parsed_json,0))
            reply = 'Added '+data+' to priority queue'

        conn.sendall(reply)

    conn.close()

def start_scraping(conn,data):
    print 'SCRAPPING! '
    
    craigslist.craigslist_scrape(data[0]['city'],data[0]['keyword'])

while 1:
    try:
        conn, addr = s.accept()
        print 'Connected with ' + addr[0] + ':' + str(addr[1])

        start_new_thread(add_to_queue ,(conn,))

    except (KeyboardInterrupt, SystemExit):
        s.close()
        sys.exit()

s.close()