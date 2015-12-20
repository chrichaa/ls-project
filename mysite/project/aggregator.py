import socket
import demjson

def scrape_data(keyword,max_price,min_price,city):
    data = {'keyword' : keyword.strip(), 'max_price' : max_price.strip(), 'min_price' : min_price.strip(), 'city' : city.strip(), 'timestamp' : 0 }
    json = demjson.encode(data)
    
    if ((keyword != 'None') and (max_price != '0')):    
        send_request(json)

def send_request(json):
    s = socket.socket()
    host = socket.gethostname()
    port = 12350

    s.connect((host, port))
    s.send(json)
    print s.recv(1024)
    s.close