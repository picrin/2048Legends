#Copyright (c) Adam Kurkiewicz 2014, all rights reserved.
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from django.http import Http404, HttpResponseServerError, HttpResponseForbidden
from django.utils import simplejson
from models import Person, Tokena, RandomNegotiation
import move_logic
import datetime
import hmac
import hashlib
import binascii
import re
import json

board = None
def index(request):
    return render(request, 'main.html', {"authenticated":True, "username":"adam"})

def play(request):
    global board
    return render(request, 'play.html')

def get_board(request):
    global board
    uid = request.GET["userid"]
    print uid
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
    response = HttpResponse(status=200)
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

def get_user(request):
    cookie = request.COOKIES.get('tokena', False)
    if not cookie:
        return HttpResponse("not logged in/ invalid token.", status=404)
    token = Tokena.objects
    token.filter(value=cookie)
    token = token.filter(active=True)
    if token:
        right_token = token[0]
        return HttpResponse(right_token.belongs_to.login, RequestContext(request), status=200)

#def magic(request):
#    pass

from ipware.ip import get_ip
#this returns 256 bits of pseudo-randomness in form of 512 bits of data.
def rand256hex():
    with open("/dev/urandom", 'rb') as f:
        return binascii.hexlify(f.read(32))

def hmachash(hashme, salt):
    hmaccer = hmac.new(str(hashme), str(salt), hashlib.sha256)
    return hmaccer.hexdigest()

def negotiate_first(request):
    #serverSecretHashed aka ID
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
    return HttpResponse(json.dumps({"serverSecretHashed": serverSecretHashed}), content_type='application/json')

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
        return HttpResponseForbidden("nice try")
    

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
            #create Token
            if observed != expected:
                return badluck
            else:
                randombytes = rand256hex()
                token = Tokena(value = randombytes, active = True, belongs_to = userrecord, created=datetime.datetime.utcnow())
                token.save()
                response = HttpResponse(status = 200)
                response.set_cookie("tokena", value=randombytes, httponly=False)
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
        return HttpResponse(200);
    else:
        return HttpResponseForbidden("username already exists")

def signin(request):
    return authenticate(request)
    #print pbkdf2.PBKDF2.crypt("hashpass", "usersalt", 10000)
    #if plainpass:
        #if not user allows plainpass:
        #    return plainpass is not allowed.
        #grab salt[username] from database
        #concat username + salt + password, and key-stretch hash
        #if not hash matches
        #    return wrong credentials
        #else
        #    generate a http-only cookie and pass it to the user, and set it to be valid for 60 minutes and reset it every
        #         time html requests are done.
        #pass
    
def signup(request):
    return create_user(request)

#def test(request):
#    board = [[1, 0, 1, 3], [0, 1, 2, 3], [0, 0, 1, 2], [2, 0, 3 ,0]]
#    move_logic.pretty_board(board)
#    result = move_logic.next_board(board, True, False)
#    move_logic.pretty_board(result["newboard"])
#ontent='', content_type=None, status=200, reason=None
#    return HttpResponse(simplejson.dumps(result), content_type='application/json')



def nextmove(request):
    global board
    direction = request.POST["direction"]
    if direction == u'1':
        booleans = (False, True)
    elif direction == u'2':
        booleans = (True, True)        
    elif direction == u'0':
        booleans = (True, False)        
    elif direction == u'3':
        booleans = (False, False)        
    else:
        raise Http404
    full_board = move_logic.next_board(board, *booleans)
    board = full_board["newboard"]
    return HttpResponse(simplejson.dumps(full_board),
                        content_type='application/json')

