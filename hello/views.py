from django.http import HttpResponse
from django.shortcuts import render

def login(request):
    response = HttpResponse();
    response.write("<p>Hello friend</p>")
    return response
