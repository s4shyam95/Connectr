from django.shortcuts import render
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from django.utils.html import escape
import json
from twilio.util import TwilioCapability
import re
import twilio.twiml

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



caller_id = "+19172596412 "

# put your default Twilio Client name here, for when a phone number isn't given
default_client = "Shyam"



@csrf_exempt
def voice(request):
    dest_number = request.GET['PhoneNumber']
    resp = twilio.twiml.Response()
    with resp.dial(callerId=caller_id) as r:
        if dest_number and re.search('^[\d\(\)\- \+]+$', dest_number):
            r.number(dest_number)
        else:
            r.client(dest_number)
    return HttpResponse(str(resp))

@csrf_exempt
def client(request):
    account_sid = "AC0fce7ce826b2ddcf434406b708fa8f32"
    auth_token = "7ed3c51485f2893e9cb980efdf3fe8ea"

    capability = TwilioCapability(account_sid, auth_token)

    application_sid = "APf6eb9001848f45a70d2f264b6f585b8d" # Twilio Application Sid
    capability.allow_client_outgoing(application_sid)
    capability.allow_client_incoming("jenny")
    token = capability.generate()
    context_dict = {}
    context_dict['token'] = token
    return render(request,'client.html', context_dict)

