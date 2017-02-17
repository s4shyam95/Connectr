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
import random

app_id = 'ac0f0c25-c0dd-4065-95d2-8ea744465bd1'
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip




def get_random_name():
    stri = "abcdefghjkmnopqrstuvwxyz"
    ret = ""
    for i in range(4):
        ret = ret + random.choice(stri)
    return ret



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
    if data["name"] == "client.slashCommand":
        text = data["text"]
        texts = (text.strip()).split(' ')
        #not really ip @name hai ye
        name = (texts[0].strip())[1:]
        name = name.lower()
        ipman = IPMan.objects.get(name=name)
        text = " ".join(texts[1:])
        g = Group.objects.get(grp_id=data["chat"])
        access = ''
        for u in User.objects.all():
            if u.grp.pk == g.pk:
                access = u.access_token
                break
        msg = Chat()
        msg.text = text
        msg.by = 1
        msg.grp = g
        msg.ip = ipman.ip
        msg.ipman = ipman
        msg.save(force_insert=True)
        text = "'"+text+"' to " + str(msg.ipman.name)
        flock_client = FlockClient(token=access, app_id=app_id)
        send_as_hal = SendAs(name=str(data["userName"]),profile_image='https://pbs.twimg.com/profile_images/1788506913/HAL-MC2_400x400.png')
        send_as_message = Message(to=g.grp_id,text=text,send_as=send_as_hal)
        res = flock_client.send_chat(send_as_message)
        return HttpResponse('{"text": "Reply Sent to User"}')

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
            context['live'] = False
            return render(request,'configure.html',context)

    company_name = (flock_client.get_user_info())['teamId']
    context = {}
    context['grps'] = grps
    context['company_name'] = company_name
    context['live'] = True
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
def new_message(request):
    grp_id = request.GET['grp_id']
    g = Group.objects.get(grp_id=grp_id)
    text = request.GET['text']
    access = ''
    for u in User.objects.all():
        if u.grp.pk == g.pk:
            access = u.access_token
            break
    msg = Chat()
    msg.text = text
    msg.by = 2
    msg.grp = g
    msg.ip = str(get_client_ip(request))
    lis = IPMan.objects.filter(ip=str(get_client_ip(request)))
    if len(lis)==0:
        ipman = IPMan()
        ipman.ip = str(get_client_ip(request))
        ipman.name = get_random_name()
        ipman.save(force_insert=True)
        msg.ipman = ipman
    else:
        msg.ipman = lis[0]
    msg.save(force_insert=True)
    flock_client = FlockClient(token=access, app_id=app_id)
    send_as_hal = SendAs(name='@'+msg.ipman.name+' on LiveChat',profile_image='https://pbs.twimg.com/profile_images/1788506913/HAL-MC2_400x400.png')
    send_as_message = Message(to=grp_id,text=text,send_as=send_as_hal)
    res = flock_client.send_chat(send_as_message)
    return HttpResponse('ok')

@csrf_exempt
def get_messages(request):
    grp_id = request.GET['grp_id']
    g = Group.objects.get(grp_id=grp_id)
    ip = str(get_client_ip(request))
    lis = Chat.objects.filter(ip=ip,grp=g)
    lst = []
    for i in lis:
        dic = {}
        dic['by'] = i.by
        dic['text'] = i.text
        lst.append(dic)
    return HttpResponse(json.dumps([dict(mpn=pn) for pn in lst]))









@csrf_exempt
def callback(request):
    return HttpResponse(str(json.dumps({'text': 'webook worked'})))







#Voice code begins here
caller_id = "+19172596412 "
default_client = "Shyam"

@csrf_exempt
def voice(request):
    # dest_number = request.POST['PhoneNumber']
    # ll = Log()
    # ll.text = str(request.POST['PhoneNumber'])
    # ll.save(force_insert=True)
    # resp = twilio.twiml.Response()
    # with resp.dial(callerId=caller_id) as r:
    #     if dest_number and re.search('^[\d\(\)\- \+]+$', dest_number):
    #         r.number(dest_number)
    #     else:
    #         r.client(dest_number)


    resp = twilio.twiml.Response()

    # Nest &lt;Client> TwiML inside of a &lt;Dial> verb
    with resp.dial(callerId=caller_id) as r:
        r.client("jenny")
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

@csrf_exempt
def incoming(request):
    resp = twilio.twiml.Response()
    # Greet the caller by name
    resp.say("Hello ")
    # Play an mp3
    resp.play("http://demo.twilio.com/hellomonkey/monkey.mp3")

    # Gather digits.
    with resp.gather(numDigits=1, action="/handle-key", method="POST") as g:
        g.say("""To speak to a real monkey, press 1.
                 Press 2 to record your own monkey howl.
                 Press any other key to start over.""")
    return HttpResponse(str(resp))

@csrf_exempt
def handle_key(request):
    """Handle key press from a user."""

    digit_pressed = request.POST['Digits']
    if digit_pressed == "1":
        resp = twilio.twiml.Response()
        resp.say("You should have pressed two mate.")
        return HttpResponse(str(resp))

    elif digit_pressed == "2":
        resp = twilio.twiml.Response()
        resp.say("Record your monkey howl after the tone.")
        resp.record(maxLength="30", action="/handle-recording")
        return HttpResponse(str(resp))

    # If the caller pressed anything but 1, redirect them to the homepage.
    else:
        resp = twilio.twiml.Response()
        resp.say("You should have pressed two mate.")
        return HttpResponse(str(resp))

@csrf_exempt
def handle_recording(request):
    """Play back the caller's recording."""
    recording_url = request.POST["RecordingUrl"]
    ll = Log()
    ll.text = str(request.POST["RecordingUrl"])
    ll.save(force_insert=True)
    resp = twilio.twiml.Response()
    resp.say("Thanks for howling... take a listen to what you howled.")
    resp.play(recording_url)
    resp.say("Goodbye.")
    return HttpResponse(str(resp))

