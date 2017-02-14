from django.shortcuts import render
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
import json
@csrf_exempt
def listen(request):
    return HttpResponse('Okay')

@csrf_exempt
def configure(request):
    return HttpResponse('welcome')


@csrf_exempt
def callback(request):
    return HttpResponse(str(json.dumps({'text': 'webook worked'})))