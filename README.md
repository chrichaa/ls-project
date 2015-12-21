# ls-project
Large Scale Web Applications Final Project     
   

## How to Run 
If running for the first time, sync the database with the django models. Cd to ls-project/mysite and run:
```
python manage.py syncdb
```
Run scrapper sever first. Cd into ls-project/mysite and run 
```
python scrapperServer.py &
```
To run server, cd into ls-project/mysite and run
```
python manage.py runserver
```
The index page should be hosted at http://127.0.0.1:8000/project/ 

## About Project
Project is an online scrapper for eBay and Craigslist data. 
Just type in the keyword for an item you would like to search, a city, and a corresponding max and min price, and it will search eBay and Craigslist for the most up to date listings. 

## How it works
When a user searches for an item, scrape_data is called in views.py. We get the keyword, max_price, min_price, city, and user_id the user searched for from the request. We then check a could conditions. 
  1. We first check if the search already exists in the database, becuase if it does, then there's no reason for us to waste time and scrape data. 
  2. If it does not exist, we call aggregator.scrape_data(), and being scraping for data. 

Aggregator.py is called with a keyword,max_price,min_price, and city. It is then given a timestamp of 0, encoded into JSON, and sent to the scrapperServer. ScrapperServer.py is always running in the background doing two things: listening for requests and keeping track of the job_queue. After aggregator.py sends its JSON object, scrapperServer will pick it up and add it to the job_queue. 

ScrapperServer.py keeps track of the job_queue in check_queue(). Here, it grabs the first object in the queue and checks it's timestamp. If the timestamp is 0, then it is a new search, and it is sent to start_scraping. If the timestamp is 15 minutes in the past, then it will also be sent to start_scraping. After start_scraping returns, the search's timestamp is updated to the current time. 

Start_scraping will then call craigslist_scrape and ebay_scrape from craigslist.py and ebay.py. Craigslist_scrape will first get the search city's closest cities from cities_dictionary.py. After getting the list of close cities, we iterate over that list, and check a few things before adding to our queue of results:
  1. First checking if a search with the same keyword, city, min_price, and max_price exist. 
    1. If it exists, which means the scrapper is just updating an old search, we create a new thread and run fetch_results(). 
  2. If it does not exist, then we search to see if there has been a similar search to the one we made.
    1. Example - If a user searches for an object between the price of $10 and $30, and another user comes around and searches for the same object, in the same city, between the price of $15 and $25, then there is no point in scraping for new data, we can just return results from the $10 to $30 search but omitting everything outside of $15 and $25. 
    2. So if a search does exist, we just add a tuple to the results queue of (city,{}).
  3. If a search does not already exist, and there are no similar searches, then we create a new thread and run fetch_results().

Fetch_Results(keyword,city,min_price,max_price,queue) first creates the corresponding city's url and grabs it's RSS feed. An empty dictionary is then created to hold the results. We then iterate through each xml entry (which would be a Craigslist posting) and grab its title, url, price, time of posting, and key. Then we add these variables to the dictionary, with a simple auto-incremented counter as the key. We create a tuple of (city, dictionary) and add it to the queue.'

After we have itterated through the list of cities, and added their corresponding (city,dict) tuples to the queue, we then itterate through the queue, changing it to a dictionary. Schema example:
  ```
        { 
            example_city : {
                auto_incremented counter : {
                    "title" : example_title
                    "url"   : example_url
                    "price" : example_price
                    "time"  : example_time
                    "key"   : example_key
                    }
                }
        }
  ```
Now that we have our dictionary, iterate through each city's items. Quickly check to see if the item is already in the database, and if it isn't, then add the item to the database. Once we finish adding a city's items, we add the search to the Craigslist_Search table in the database. craigslist.py is now done, we just return the number of items we found.

After craigslist.py returns, we move on to ebay.py's ebay_scrape. ebay_scrape calls fetch_results, where we make an API call using eBay's SDK. We then return the same as craiglist.py (title,url,price,key) and create a dictionary of the results. We then iterate through the dictionary of results, adding them to the database if it is not already in there. ebay.py then returns its number of results. We are now done with ebay.py

start_scraping is then done, and we are now back in check_queue in scrapperServer.py. We then update the search's timestamp to the current time and move it to the back of the job_queue.

Now that the search and its results have been added to the database, we should exit out of the loop in views.py scrape_data. The database is now queried for the results that we searched for, and then the HTML table is populated. We are done with a search. 
