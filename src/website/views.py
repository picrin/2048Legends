#Copyright (c) Adam Kurkiewicz 2014, all rights reserved.
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from django.http import Http404, HttpResponseServerError, HttpResponseForbidden
from django.utils import simplejson
from models import Person, Tokena, Game, Move
import move_logic
import datetime
import hmac
import hashlib
import binascii
import re
import json

board = None
def processToRender(request, *args, **kwargs):
    """
    get_user__response = get_user(request)
    print dir(get_user__response)
    templateData = {}
    if get_user__response.status_code == 200:
        templateData["authenticated"] = True
    else:
        templateData["authenticated"] = False
    templateData["username"] = get_user__response.content
    """
    pass
def index(request):
    get_user__response = get_user(request)
    print dir(get_user__response)
    templateData = {}
    if get_user__response.status_code == 200:
        templateData["authenticated"] = True
    else:
        templateData["authenticated"] = False
    templateData["username"] = get_user__response.content
    return render(request, 'main.html', templateData)

def play(request):
    global board
    return render(request, 'play.html')

def get_board(request):
    global board
    uid = request.GET["userid"]
    if board == None:
        board = move_logic.create_board(move_logic.size)
        board[2][2] = 2
    resp = {}
    resp["board"] = board
    resp["gameid"] = 107
    return HttpResponse(simplejson.dumps(resp), content_type='application/json')    

def login(request):
    return render(request, "login.html")

def logout(request):
    response = render(request, 'main.html')
    response.delete_cookie('tokena')
    return response
    
def magic(request):
    p1 = Person(login = "picrin", hashedPassword = "similar")
    p1.save()

    k1 = Tokena(value = "please come in", active = True, belongs_to = p1, created=datetime.datetime.utcnow())
    k1.save()
    k2 = Tokena(value = "you're not welcome", active = False, belongs_to = p1, created=datetime.datetime.utcnow())
    k2.save()
    print k1
    print k2
    return HttpResponse("nice", RequestContext(request))

def get_user(request, just_username = False):
    cookie = request.COOKIES.get('tokena', False)
    if not cookie:
        return HttpResponse("not logged in/ invalid token.", status=404)
    token = Tokena.objects
    token = token.filter(value=cookie)
    token = token.filter(active=True)
    if token:
        right_token = token[0]
        print "-"*80
        print len(token)
        print right_token.belongs_to.login
        return HttpResponse(right_token.belongs_to.login, RequestContext(request), status=200)

from ipware.ip import get_ip

#this returns 256 bits of pseudo-randomness in form of 512 bits of data.
def rand256hex():
    with open("/dev/urandom", 'rb') as f:
        return binascii.hexlify(f.read(32))

def hmachash(hashme, salt):
    hmaccer = hmac.new(str(hashme), str(salt), hashlib.sha256)
    return hmaccer.hexdigest()

def negotiate_first(request):
    clientSecretHashed = str(request.POST["clientSecretHashed"])
    serverSecret = rand256hex()
    hasher = hashlib.sha256()
    hasher.update(serverSecret)
    serverSecretHashed = hasher.hexdigest()
    print serverSecretHashed
    negotiation = RandomNegotiation(
            serverSecret = serverSecret,
            serverSecretHashed = serverSecretHashed,
            clientSecret = "",
            clientSecretHashed = clientSecretHashed
            )
    negotiation.save()
    return serverSecretHashed
    #return HttpResponse(json.dumps({"serverSecretHashed": }), content_type='application/json')

def negotiate_second(request):
    clientSecret = str(request.POST["clientSecret"])
    serverSecretHashed = str(request.POST["serverSecretHashed"])
    negotiationManager = RandomNegotiation.objects
    negotiationManager.filter(serverSecretHashed = serverSecretHashed)
    records = negotiationManager.filter(clientSecret = "")
    if records:
        record = records[0]
        record.clientSecret = clientSecret
        record.save()
        secret = record.serverSecret
        return HttpResponse(json.dumps({"serverSecret": secret}), content_type='application/json')
    else:
        return HttpResponseForbidden("Pacta sunt servanda")
    
def authenticate(request):
    #ip = get_ip(request)
    username = str(request.POST["username"])
    password = str(request.POST["password"])
    if not re.match("^\w{3,16}$", username):
        return HttpResponseForbidden("username needs to have between 3-16 alphanumeric or underscore characters")
    #print str(username)
    bylogin = Person.objects.filter(login = str(username))
    print bylogin
    badluck = HttpResponseForbidden("wrong username/password")
    if bylogin:
        if len(bylogin) == 1:
            userrecord = bylogin[0]
            print userrecord
            observed = hmachash(password, userrecord.salt)
            expected = userrecord.hashedPassword
            print "observed:", observed
            print "expected:", expected
            if observed != expected:
                return badluck
            else:
                randombytes = rand256hex()
                token = Tokena(value = randombytes, active = True, belongs_to = userrecord, created=datetime.datetime.utcnow())
                token.save()
                response = HttpResponse(status = 200)
                response.set_cookie("tokena", value=randombytes, httponly=True)
                return response
        else:
            return HttpResponseServerError("couldn't authenticate the user, username non-ambiguous.")
    else:
        return badluck

#str(hex(int("3702fc",16) ^ int("4f9db7",16)))[2:-1]     
def create_user(request):
    #ip = get_ip(request)
    username = request.POST["username"]
    password = request.POST["password"]
    if not re.match("^\w{3,16}$", username):
        return HttpResponseForbidden("username needs to have between 3-16 alphanumeric or underscore characters")
    #print str(username)
    bylogin = Person.objects.filter(login = str(username))
    print bylogin
    if not bylogin:
        salt = rand256hex()
        hashedpass = hmachash(password,salt)
        newPerson=Person(login = username, hashedPassword = hashedpass, salt=salt)
        newPerson.save()
        return HttpResponse(status = 200);
    else:
        return HttpResponseForbidden("username already exists")

def signin(request):
    return authenticate(request)

def signup(request):
    return create_user(request)

#def test(request):
#    board = [[1, 0, 1, 3], [0, 1, 2, 3], [0, 0, 1, 2], [2, 0, 3 ,0]]
#    move_logic.pretty_board(board)
#    result = move_logic.next_board(board, True, False)
#    move_logic.pretty_board(result["newboard"])
#ontent='', content_type=None, status=200, reason=None
#    return HttpResponse(simplejson.dumps(result), content_type='application/json')

def register(request):
    return render(request, "register.html")

def nextmove(request):
    global board
    print board
    direction = request.POST["direction"]
    if direction == "right":
        booleans = (False, True)
    elif direction == "down":
        booleans = (True, True)
    elif direction == "up":
        booleans = (True, False)
    elif direction == "left":
        booleans = (False, False)
    else:
        raise Http404
    full_board = move_logic.next_board(board, *booleans)
    #print full_board
    board = full_board["newboard"]
    
    serverSecretHashed = negotiate_first(request)
    full_board["serverSecretHashed"] = serverSecretHashed;
    return HttpResponse(json.dumps(full_board),
                        content_type='application/json')

