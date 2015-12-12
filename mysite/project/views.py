from django.shortcuts import render
from django.http import HttpResponse
from pymongo import MongoClient
import aggregator

def index(request):
    return render(request, 'project/index.html')

def register(request):
    return render(request, 'project/register.html')

def dashboard(request):
    client = MongoClient('localhost', 27017)
    db = client.largescale

    #Get current user's searches and fetch results from mongo tables
    #Refresh HTML table with results 

    return render(request, 'project/dashboard.html')

def scrape_data(request):
    if request.GET['term']:
        keyword = request.GET['term']
    else:
        keyword = 'None'

    if request.GET['maxprice']:
        max_price = request.GET['maxprice']
    elif (int(request.GET['maxprice']) > 999999):
        max_price = '999999.99'
    else:
        max_price = '999999.99'

    if request.GET['minprice']:
        min_price = request.GET['minprice']
    else:
        min_price = '0'
    print request.GET['citydrop']

    city      = 'newyork'
    user      = 'tmp_user'

    aggregator.scrape_data(keyword,max_price,min_price,city,user)

    #Think this has to be changed
    return render(request, 'project/dashboard.html')
