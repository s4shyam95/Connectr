from django.shortcuts import render
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from django.utils.html import escape
import json
@csrf_exempt
def listen(request):
    print escape(repr(request))
    return HttpResponse('listen')

@csrf_exempt
def configure(request):
    print 'bullshit' + escape(repr(request))
    return HttpResponse('configured')


@csrf_exempt
def callback(request):
    return HttpResponse(str(json.dumps({'text': 'webook worked'})))