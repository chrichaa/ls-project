from django.shortcuts import render
from django.http import HttpResponse
import aggregator

def index(request):
    return render(request, 'project/index.html')

def register(request):
    return render(request, 'project/register.html')

def dashboard(request):
    return render(request, 'project/dashboard.html')

def scrape_data(request):
    if request.GET['term']:
        keyword = request.GET['term']
    else:
        keyword = 'None'

    if request.GET['maxprice']:
        max_price = request.GET['maxprice']
    else:
        max_price = '0'

    min_price = '0'
    city      = 'newyork'
    user      = 'tmp_user'

    aggregator.scrape_data(keyword,max_price,min_price,city,user)

    #Think this has to be changed
    context = {}
    return render(request, 'project/dashboard.html', context)
