from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext

def index(request):
    return render(request, 'main.html', RequestContext(request))

def play(request):
    return render(request, 'play.html', RequestContext(request))

def nextmove(request):
    print request.POST
    return HttpResponse(request.POST["direction"])

