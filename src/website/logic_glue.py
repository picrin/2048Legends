from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from django.http import Http404, HttpResponseServerError, HttpResponseForbidden
from models import Person, Tokena, Game, Move
import move_logic
import datetime
import hmac
import hashlib
import binascii
import re
import json
import move_logic

def processAndRender(request, path, templateVars = {}):
    username = token_to_username(request)
    templateData = {}
    if username is not None:
        templateData["authenticated"] = True
        templateData["username"] = username
    templateVars.update(templateData)
    return render(request, path, templateVars)

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

def retrieve_token(request, delete = False):
    cookie = request.COOKIES.get('tokena', False)
    if not cookie:
        return None
    token = Tokena.objects
    token = token.filter(value=cookie)
    token = token.filter(active=True)
    if token:
        right_token = token[0]
        if delete:
            right_token.active = False
            right_token.save()
        return right_token
    else:
        return None

def token_to_username(request):
    token = retrieve_token(request)
    if token is not None:
        return token.belongs_to.login
    return None
    
def token_to_user(request):
    token = retrieve_token(request)
    if token is not None:
        return token.belongs_to
    return None

def rand256hex():
    with open("/dev/urandom", 'rb') as f:
        return binascii.hexlify(f.read(32))

def hmachash(hashme, salt):
    hmaccer = hmac.new(str(hashme), str(salt), hashlib.sha256)
    return hmaccer.hexdigest()

def authenticate(request):
    #TODO timing attack to discover usernames
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

class UnfinishedMove(Exception):
    pass

def negotiate_first(game, resolved_board, clientSecretHashed):
    previousMove = game.lastMove
    if previousMove.clientSecret == "":
        raise UnfinishedMove("I was expecting client secret now.")
    previousNumber = previousMove.moveNumber
    serverSecret = rand256hex()
    hasher = hashlib.sha256()
    hasher.update(serverSecret)
    serverSecretHashed = hasher.hexdigest()
    move = Move(
            belongs_to = game,
            moveNumber = previousNumber + 1,
            board = move_logic.serialize_board(resolved_board),
            serverSecret = serverSecret,
            serverSecretHashed = serverSecretHashed,
            clientSecret = "",
            clientSecretHashed = clientSecretHashed
            )
    move.save()
    game.lastMove = move
    game.save()
    return game
    #return HttpResponse(json.dumps({"serverSecretHashed": }), content_type='application/json')
def negotiate_second(game, clientSecret):
    move = game.lastMove
    if move.clientSecret != "":
        raise UnfinishedMove("I was expecting client comittment now")
    else:
        move.clientSecret = clientSecret
        move.save()
#        negotiationManager.filter(serverSecretHashed = serverSecretHashed)
 #       records = negotiationManager.filter(clientSecret = "")
  #      if records:
   #         record = records[0]
    #        record.clientSecret = clientSecret
     #       record.save()
      #      secret = record.serverSecret
       #     return HttpResponse(json.dumps({"serverSecret": secret}), content_type='application/json')
    return move
    
def check_validity(move): # isValid, randomNumber
    return { "valid": True,
             "serverSecret": "secret",
             "randomNumber": rand256hex(),
             "position": 123,
             "value": 1
            }