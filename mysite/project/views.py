from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'project/index.html')

def register(request):
    return render(request, 'project/register.html')

def dashboard(request):
    return render(request, 'project/dashboard.html')
