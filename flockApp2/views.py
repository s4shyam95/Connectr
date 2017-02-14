from django.shortcuts import render
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from django.utils.html import escape
import json, jwt
from twilio.util import TwilioCapability
import re
import twilio.twiml
from flockApp2.models import *
from pyflock import FlockClient, verify_event_token
from pyflock import Message, SendAs, Attachment, Views, WidgetView, HtmlView, ImageView, Image, Download, Button, OpenWidgetAction, OpenBrowserAction, SendToAppAction


app_id = 'ac0f0c25-c0dd-4065-95d2-8ea744465bd1'
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip








@csrf_exempt
def listen(request):
    data = json.loads(request.body)
    if data["name"] == "app.install":
        u = User()
        u.access_token = data["token"]
        u.user_id = data["userId"]
        u.save(force_insert=True)
    if data["name"] == "app.uninstall":
        u = User.objects.get(user_id=data["userId"])
        u.delete()
    return HttpResponse('listen')

@csrf_exempt
def configure(request):
    secret = 'fe55371c-2da7-415a-9804-c531ffa000e7'
    encoded = request.GET['flockEventToken']
    data = jwt.decode(encoded, secret, algorithms=['HS256'])
    user_id = data['userId']
    u = User.objects.get(user_id=user_id)
    flock_client = FlockClient(token=u.access_token, app_id=app_id)
    grps = flock_client.get_groups()
    for i in grps:
        ret = Group.objects.filter(grp_id=i['id'])
        if len(ret) > 0:
            context = {}
            u.grp = ret[0]
            u.save()
            context['grp'] = ret[0]
            return render(request,'already.html',context)

    company_name = (flock_client.get_user_info())['teamId']
    context = {}
    context['grps'] = grps
    context['company_name'] = company_name
    return render(request,'configure.html',context)
    # return HttpResponse('bullshit' + escape(repr(request)))

@csrf_exempt
def new_group(request):
    grp_id = request.GET['grp_id']
    company_name = request.GET['company_name']
    grp_name = request.GET['grp_name']
    g = Group()
    g.grp_id = grp_id
    g.company = company_name
    g.group_name = grp_name
    g.save(force_insert=True)
    for u in User.objects.all():
        if u.grp is None:
            u.grp = g
            u.save()
    return HttpResponse('ok')


@csrf_exempt
def callback(request):
    return HttpResponse(str(json.dumps({'text': 'webook worked'})))







#Voice code begins here
caller_id = "+19172596412 "
default_client = "Shyam"

@csrf_exempt
def voice(request):
    dest_number = request.POST['PhoneNumber']
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

