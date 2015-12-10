# Aggregator
import socket
import demjson

def main():
    for_testing()

def for_testing():
    keyword   = raw_input('Enter keyword: ')
    max_price = raw_input('Enter maxprice: ')
    min_price = raw_input('Enter minprice: ')
    city      = raw_input('Enter city: ')
    user      = raw_input('Enter user: ')

    data = { 'keyword' : keyword.replace(' ','%20'), 'max_price' : max_price, 'min_price' : min_price, 'city' : city, 'user' : user, 'timestamp' : 0 }
    json = demjson.encode(data)
    
    send_request(json)

def send_request(json):
    s = socket.socket()         # Create a socket object
    host = socket.gethostname() # Get local machine name
    port = 12347                # Reserve a port for your service.

    s.connect((host, port))
    s.send(json)
    print s.recv(1024)
    s.close                     # Close the socket when done



main()
