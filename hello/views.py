from django.http import HttpResponse
from django.shortcuts import render

def hello(request):
    response = HttpResponse();
    response.write("<p>Hello friend</p>")
    return response
