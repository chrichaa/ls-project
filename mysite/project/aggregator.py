# Aggregator
import socket
import demjson

#def main():
#    for_testing()

def scrape_data(keyword,max_price,min_price,city,user):
#    keyword   = raw_input('Enter keyword: ')
#    max_price = raw_input('Enter maxprice: ')
#    min_price = raw_input('Enter minprice: ')
#    city      = raw_input('Enter city: ')
#    user      = raw_input('Enter user: ')

    data = { 'keyword' : keyword.strip(), 'max_price' : max_price.strip(), 'min_price' : min_price.strip(), 'city' : city.strip(), 'user' : user.strip(), 'timestamp' : 0 }
    json = demjson.encode(data)
    
    if ((keyword != 'None') and (max_price != '0')):    
        send_request(json)

def send_request(json):
    s = socket.socket()         # Create a socket object
    host = socket.gethostname() # Get local machine name
    port = 12348                # Reserve a port for your service.

    s.connect((host, port))
    s.send(json)
    print s.recv(1024)
    s.close                     # Close the socket when done



#main()
