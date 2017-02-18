import urllib

from django.shortcuts import render
from django.http.response import HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
import os
import json, jwt
import time
from twilio.util import TwilioCapability
from twilio.rest import TwilioRestClient
import re
import twilio.twiml
from flockApp2.models import *
from pyflock import FlockClient, Download, Views, Attachment
from pyflock import Message, SendAs
import random
import speech_recognition as sr
from django.urls import reverse

# Voice code begins here
caller_id = "+19172596412 "
default_client = "Shyam"

from flockProj2.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_DEFAULT_CALLERID, APPLICATION_SID

digits_dict = {
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine",
    "0": "zero",
    "*": "star",
    "#": "hash",
}


def log(s):
    s = str(s)
    ll = Log()
    ll.text = s
    ll.save(force_insert=True)


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
        # not really ip @name hai ye
        g = Group.objects.get(grp_id=data["chat"])
        access = ''
        for u in User.objects.all():
            if u.grp.pk == g.pk:
                access = u.access_token
                break

        if (texts[0].strip())[0] != '@':
            # take last message where by = 2, and set that as ipman
            log("here")
            lis = Chat.objects.filter(by=2)
            last_msg = lis[len(lis) - 1]
            log(last_msg)
            ipman = last_msg.ipman
            log("ipname is " + ipman.name)
            text = " ".join(texts)
            log("text is " + str(text))
            msg = Chat()
            msg.text = text
            msg.by = 1
            msg.grp = g
            msg.ip = ipman.ip
            msg.ipman = ipman
            msg.save(force_insert=True)
            text = "'" + text + "' to " + str(msg.ipman.name)
            flock_client = FlockClient(token=access, app_id=app_id)
            send_as_hal = SendAs(name=str(data["userName"]),
                                 profile_image='https://pbs.twimg.com/profile_images/1788506913/HAL-MC2_400x400.png')
            send_as_message = Message(to=g.grp_id, text=text, send_as=send_as_hal)
            res = flock_client.send_chat(send_as_message)
            return HttpResponse('{"text": "Reply Sent to User"}')
        else:
            name = (texts[0].strip())[1:]
            name = name.lower()
            ipman = IPMan.objects.get(name=name)
            text = " ".join(texts[1:])
            msg = Chat()
            msg.text = text
            msg.by = 1
            msg.grp = g
            msg.ip = ipman.ip
            msg.ipman = ipman
            msg.save(force_insert=True)
            text = "'" + text + "' to " + str(msg.ipman.name)
            flock_client = FlockClient(token=access, app_id=app_id)
            send_as_hal = SendAs(name=str(data["userName"]),
                                 profile_image='https://pbs.twimg.com/profile_images/1788506913/HAL-MC2_400x400.png')
            send_as_message = Message(to=g.grp_id, text=text, send_as=send_as_hal)
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
    flag = 0
    rett = None
    for i in grps:
        ret = Group.objects.filter(grp_id=i['id'])
        if len(ret) > 0:
            flag = 1
            rett = ret[0]
    context = {}
    if flag == 1:
        u.grp = rett
        u.save()
        context['grp'] = rett
        context['live'] = False
    else:

        context['grps'] = grps

        context['live'] = True

    company_name = (flock_client.get_user_info())['teamId']
    context['company_name'] = company_name
    ccs = Company.objects.filter(team_id=company_name)

    if not ccs:
        context['call'] = True
        context['grps'] = grps
    else:
        context['call'] = False
        cc = ccs[0]
        context['routes'] = Route.objects.filter(flock_group__company=cc)

    context['access_token'] = u.access_token
    return render(request, 'configure.html', context)
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
    if len(lis) == 0:
        ipman = IPMan()
        ipman.ip = str(get_client_ip(request))
        ipman.name = get_random_name()
        ipman.save(force_insert=True)
        msg.ipman = ipman
    else:
        msg.ipman = lis[0]
    msg.save(force_insert=True)
    flock_client = FlockClient(token=access, app_id=app_id)
    send_as_hal = SendAs(name='@' + msg.ipman.name + ' on LiveChat',
                         profile_image='https://pbs.twimg.com/profile_images/1788506913/HAL-MC2_400x400.png')
    send_as_message = Message(to=grp_id, text=text, send_as=send_as_hal)
    res = flock_client.send_chat(send_as_message)
    return HttpResponse('ok')


@csrf_exempt
def get_messages(request):
    grp_id = request.GET['grp_id']
    g = Group.objects.get(grp_id=grp_id)
    ip = str(get_client_ip(request))
    lis = Chat.objects.filter(ip=ip, grp=g).order_by('pk')
    lst = []
    for i in lis:
        dic = {}
        dic['by'] = i.by
        dic['text'] = i.text
        lst.append(dic)
    return HttpResponse(json.dumps([dict(mpn=pn) for pn in lst]))


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
@xframe_options_exempt
def client(request):
    account_sid = TWILIO_ACCOUNT_SID
    auth_token = TWILIO_AUTH_TOKEN
    capability = TwilioCapability(account_sid, auth_token)
    application_sid = APPLICATION_SID
    capability.allow_client_outgoing(application_sid)
    token = capability.generate()
    context_dict = {}
    context_dict['token'] = token
    return render(request, 'client.html', context_dict)


@csrf_exempt
def wait_music(request):
    twilio_waiting_response = twilio.twiml.Response()
    twilio_waiting_response.play(url='http://com.twilio.sounds.music.s3.amazonaws.com/MARKOVICHAMP-Borghestral.mp3')
    return HttpResponse(str(twilio_waiting_response))


@csrf_exempt
def incoming(request):
    twilio_response = twilio.twiml.Response()
    companies = Company.objects.filter(number=TWILIO_DEFAULT_CALLERID)
    company = companies[len(companies) - 1]
    log(str(len(companies)) + " companies")
    with twilio_response.gather(action='/handle_ivr/', numDigits=1) as g:
        g.say('Welcome to ' + company.name + "'s quick support")
        routes = Route.objects.filter(flock_group__company=company).order_by('pk')
        log(str(len(routes)) + " routes")
        say_string = ''
        for r in routes:
            say_string += 'Press ' + digits_dict.get(r.digits,
                                                     "ERROR") + ' to connect to ' + r.flock_group.group_name + "team ."
        g.say(say_string)
        g.pause(length=10)
        # g.say(say_string)
    return HttpResponse(str(twilio_response))


@csrf_exempt
def handle_ivr(request):
    callsid = request.POST["CallSid"]
    digits = request.POST.get('Digits', '')
    number = request.POST.get('From', '')
    twilio_response = twilio.twiml.Response()
    companies = Company.objects.filter(number=TWILIO_DEFAULT_CALLERID).order_by('pk')
    company = companies[len(companies) - 1]
    group_name = 'customer support'
    if digits:
        route = Route.objects.filter(flock_group__company=company, digits=digits).order_by('pk')[0]
        if route:
            mob_user = MobUser.objects.filter(number=number).order_by('pk')
            if not mob_user:
                mob_user = MobUser(number=number)
            else:
                mob_user = mob_user[0]
            mob_user.interaction = digits
            mob_user.call_sid = callsid
            mob_user.save()
            group_name = route.flock_group.group_name

        connect_sucessful = "You are now connected to " + company.name + "'s " + group_name + " team." + \
                            " Please explain your query in brief after the tone and press hash to finish."
        twilio_response.say(connect_sucessful)
        twilio_response.record(maxLength="120", playBeep="true", action="/handle-recording", finishOnKey='#',
                               transcribe='true', transcribeCallback='/transcribe_handle')
        twilio_response.say(
            "Sorry, we didn't get your recording. Please try again after the tone and press hash to finish.")
        twilio_response.record(maxLength="120", playBeep="true", action="/handle-recording", finishOnKey='#',
                               transcribe='true', transcribeCallback='/transcribe_handle')
        twilio_response.say("Sorry, we didn't get your recording. Please try again later")
        twilio_response.hangup()
    else:
        with twilio_response.gather(action='/handle_ivr/', numDigits=1) as g:
            routes = Route.objects.filter(flock_group__company=company).order_by('pk')
            say_string = ''
            for r in routes:
                say_string += 'Press ' + digits_dict.get(r.digits, "ERROR") + ' to connect to ' + r.group_name + \
                              "team ."
            g.say(say_string)
    return HttpResponse(str(twilio_response))


# Paren will send me data from front end, save it
@csrf_exempt
def save_interactions(request):
    company_name = request.POST['company_name']
    team_id = request.POST['team_id']
    access_token = request.POST['access_token']
    c = Company.objects.filter(team_id=team_id).order_by('pk')
    if not c:
        c = Company()
        c.team_id = team_id
    else:
        c = c[0]
    c.access_token = access_token
    c.name = company_name
    c.number = TWILIO_DEFAULT_CALLERID
    c.save()
    interactions = request.POST['interactions']
    interactions = json.loads(interactions)
    for i in interactions:
        r = Route()
        r.digits = i["number"]
        flock_group = FlockGroup()
        flock_group.access_token = access_token
        flock_group.group_name = i["group_name"]
        flock_group.group_id = i["group_id"]
        flock_group.company = c
        flock_group.save()
        r.flock_group = flock_group
        r.save()
    return HttpResponse('ok')


@csrf_exempt
def incomingWidget(request):
    callsid = request.GET['callsid']
    group_id = request.GET['group_id']
    account_sid = TWILIO_ACCOUNT_SID
    auth_token = TWILIO_AUTH_TOKEN
    capability = TwilioCapability(account_sid, auth_token)
    application_sid = APPLICATION_SID
    capability.allow_client_incoming(callsid)
    token = capability.generate()
    context_dict = {}
    context_dict['token'] = token
    context_dict['group_id'] = group_id
    # TODO
    # change this to incoming call
    return render(request, 'client.html', context_dict)


@csrf_exempt
def callupdate(request):
    callsid = request.POST['callsid']
    group_id = request.POST['group_id']
    account_sid = TWILIO_ACCOUNT_SID
    auth_token = TWILIO_AUTH_TOKEN
    client = TwilioRestClient(account_sid, auth_token)
    gimme_url = "https://peaceful-hollows-95315.herokuapp.com/gimme/?callsid=" + callsid + '&group_id=' + \
                group_id.split(':')[1]
    call = client.calls.update(
        callsid,
        url=gimme_url,
        method="POST")
    return HttpResponse(str(call.to))


@csrf_exempt
def gimme(request):
    resp = twilio.twiml.Response()
    callsid = request.GET['callsid']
    group_id = request.GET['group_id']
    resp.say('This call will be recorded for training purposes.')
    with resp.dial(callerId=caller_id, record="record-from-answer-dual",
                   action="/callrecording/" + group_id + "/") as r:
        r.client(callsid)
    return HttpResponse(str(resp))


@csrf_exempt
def callrecording(request, group='ERROR'):
    group = "g:" + group
    group = group.strip()
    url = request.POST['RecordingUrl']
    callsid = request.POST['CallSid']
    log(group)
    fg = FlockGroup.objects.get(group_id=group)

    d = Download(src=url)
    views = Views()
    views.add_flockml("<flockml>Download the <i>Audio Recording</i></flockml>")
    flock_client = FlockClient(token=fg.access_token, app_id=app_id)
    send_as_hal = SendAs(name='@CallRecorder',
                         profile_image='https://pbs.twimg.com/profile_images/1788506913/HAL-MC2_400x400.png')

    attachment = Attachment(title="Audio Recording from Call", downloads=[d], views=views)
    files_message = Message(to=fg.group_id, attachments=[attachment], send_as=send_as_hal)
    res = flock_client.send_chat(files_message)
    log(res)
    resp = twilio.twiml.Response()
    resp.say("Goodbye")
    return HttpResponse(str(resp))


@csrf_exempt
def transcribed(request):
    callsid = request.POST['CallSid']
    text = request.POST['TranscriptionText']
    log("From Twilio: " + text)
    # send text to flock,
    companies = Company.objects.filter(number=TWILIO_DEFAULT_CALLERID).order_by('pk')
    company = companies[len(companies) - 1]
    lis = MobUser.objects.filter(call_sid=callsid).order_by('pk')
    mobuser = lis[0]
    r = Route.objects.filter(digits=mobuser.interaction, flock_group__company=company).order_by('pk')[0]

    flock_client = FlockClient(token=r.flock_group.access_token, app_id=app_id)
    send_as_hal = SendAs(name='@' + mobuser.number + ' on Call',
                         profile_image='https://pbs.twimg.com/profile_images/1788506913/HAL-MC2_400x400.png')

    # send attachment here, not message!, on click of that button, do callupdate!
    send_as_message = Message(to=r.flock_group.group_id, text=text + ' ~ ' + callsid, send_as=send_as_hal)
    res = flock_client.send_chat(send_as_message)
    return HttpResponse('ok')


def save_recording(recording_url, callsid):
    log("deleting file")
    try:
        os.remove('Twilio.wav')
    except OSError:
        pass
    log("downloading begins")

    try:
        # r = requests.get(recording_url, stream=True)
        # if r.status_code == 200:
        # with open(os.path.join('/tmp', 'twi_audio.wav'), 'wb') as f:
        # # for block in r.iter_content(1024):
        #     # f.write(block)
        #     r.raw.decode_content = True
        #     shutil.copyfileobj(r.raw, f)
        # f.close()
        # # os.system("wget -O Twilio.wav " + recording_url)
        # # time.sleep(5)
        urllib.urlretrieve(recording_url, "Twilio.wav")
        time.sleep(10)
    except Exception, e:
        log('t1' + e.message)

    if not os.path.exists('Twilio.wav'):
        log('FUCKCKCKCKCKCKCK')

    log("reco begins")
    reco = sr.Recognizer()
    text = "prob"
    try:
        with sr.AudioFile('Twilio.wav') as source:  # use "test.wav" as the audio source
            audio = reco.record(source)  # extract audio data from the file
        try:
            text = reco.recognize_google(audio, language="en-us", show_all=False)
            log("text is " + str(text))
        except LookupError:  # speech is unintelligible
            text = "Problem understanding"
            log(text)
            # print("Could not understand audio")
    except Exception, e:
        log('t2' + e.message)


    # send text to flock,
    companies = Company.objects.filter(number=TWILIO_DEFAULT_CALLERID).order_by('pk')
    company = companies[len(companies) - 1]
    lis = MobUser.objects.filter(call_sid=callsid).order_by('pk')
    mobuser = lis[0]
    r = Route.objects.filter(digits=mobuser.interaction, flock_group__company=company).order_by('pk')[0]

    flock_client = FlockClient(token=r.flock_group.access_token, app_id=app_id)
    send_as_hal = SendAs(name='@' + mobuser.number + ' on Call',
                         profile_image='https://pbs.twimg.com/profile_images/1788506913/HAL-MC2_400x400.png')

    # send attachment here, not message!, on click of that button, do callupdate!
    send_as_message = Message(to=r.flock_group.group_id, text=text + ' ~ ' + callsid, send_as=send_as_hal)
    res = flock_client.send_chat(send_as_message)


@csrf_exempt
def handle_recording(request):
    """Play back the caller's recording."""
    log("reached handle recording")
    callsid = request.POST['CallSid']
    recording_url = request.POST["RecordingUrl"]

    twilio_response = twilio.twiml.Response()
    twilio_response.say("Your query has been sent to the team. You will now be connected to a customer sales"
                        " representative. Please hold the line")
    twilio_response.enqueue(waitUrl=request.build_absolute_uri(reverse('wait_music')), waitUrlMethod='POST',
                            name='wait_')

    # threading.Thread(target=save_recording, args=(recording_url, callsid,)).start()
    return HttpResponse(str(twilio_response))

