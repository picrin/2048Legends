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

def newGame(user):
    board = move_logic.create_board(move_logic.size)
    board[1][1] = 1
    move = Move(
            belongs_to = None,
            moveNumber = 1,
            board = move_logic.serialize_board(board),
            serverSecret = "0",
            serverSecretHashed = "0",
            clientSecret = "0",
            clientSecretHashed = "0"
            )
    move.save()
    game = Game(
            gameid = rand256hex(),
            belongs_to = user,
            gameover = False,
            lastMove = move
            )
    game.save()
    move.belongs_to = game
    move.save()
    return game

def processAndRender(request, path, templateVars = None):
    if templateVars is None:
        templateVars = {}
    user = token_to_user(request)
    print "username", username
    templateData = {}
    if user is not None:
        username = user.login
        templateData["authenticated"] = True
        templateData["username"] = username
        templateData["plays_remaining"] = user.gamesRemaining
    else:
        templateData["authenticated"] = False
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

def cookie_to_game(request):
    gameid = request.COOKIES.get("gameid")
    if gameid is None:
        return None
    game = Game.objects.filter(gameid=gameid)
    if game:
        return game[0]
    else:
        return None


def token_to_game(request):
    user = token_to_user(request)
    if user is None:
        return None, cookie_to_game(request)
    else:
        return user, user.currentGame

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
    badluck = HttpResponseForbidden("wrong username/password")
    if bylogin:
        if len(bylogin) == 1:
            userrecord = bylogin[0]
            observed = hmachash(password, userrecord.salt)
            expected = userrecord.hashedPassword
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

def create_user(request):
    #ip = get_ip(request)
    username = request.POST["username"]
    password = request.POST["password"]
    #, 
    if not re.match("^\w{3,16}$", username) or any([re.search(disallowed, username) for disallowed in ["^anonymous$", "^admin$", "^administrator$", "^moderator$", "^picrin$", "^kutykula$", "adam", "kurkiewicz", "kurkeiwicz"]]):
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

def sha256(string):
    hasher = hashlib.sha256()
    hasher.update(string)
    return hasher.hexdigest()

def negotiate_first(game, resolved_board, allempty, clientSecretHashed):
    previousMove = game.lastMove
    if previousMove.clientSecret == "":
        raise UnfinishedMove("I was expecting client secret now.")
    previousNumber = previousMove.moveNumber
    serverSecret = rand256hex()
    serverSecretHashed = sha256(serverSecret)
    move = Move(
            belongs_to = game,
            moveNumber = previousNumber + 1,
            board = move_logic.serialize_board(resolved_board),
            allempty = move_logic.serialize_board(allempty),
            serverSecret = serverSecret,
            serverSecretHashed = serverSecretHashed,
            clientSecret = "",
            clientSecretHashed = clientSecretHashed
            )
    move.save()
    game.lastMove = move
    game.save()
    return move
    #return HttpResponse(json.dumps({"serverSecretHashed": }), content_type='application/json')

def xorHex(string1, string2):
    if len(string1) != len(string2) != 64:
        raise HttpResponseServerError("xored objects need to be 256 bits/ 64 hex-digits")
    inHex = format(int(string1, 16) ^ int(string2, 16), "x")
    return "0" * (64 - len(inHex)) + inHex
    #that's probably more inefficient
    #zipped = zip(string1, string2)
    #for index, tupla in enumerate(zipped):
    #    inter = lambda hexInt: int(hexInt, 16)
    #    asInts = map(inter, tupla)
    #    xored = asInts[0] ^ asInts[1]
    #    asHex = hex(xored)
    #    zipped[index] = asHex
    #print "joined", "".join([string[-1] for string in zipped])
    

def negotiate_second(game, clientSecret):
    move = game.lastMove
    if move.clientSecret != "":
        raise UnfinishedMove("I was expecting client comittment now")
    else:
        move.clientSecret = clientSecret
        
#        negotiationManager.filter(serverSecretHashed = serverSecretHashed)
 #       records = negotiationManager.filter(clientSecret = "")
  #      if records:
   #         record = records[0]
    #        record.clientSecret = clientSecret
     #       record.save()
      #      secret = record.serverSecret
       #     return HttpResponse(json.dumps({"serverSecret": secret}), content_type='application/json')
    return check_validity(move)

def check_validity(move): # isValid, randomNumber
    clientSecret = move.clientSecret
    clientSecretHashed = move.clientSecretHashed
    valid = (sha256(clientSecret) == clientSecretHashed)
    if valid:
        serverSecret = move.serverSecret
        randomNumber = xorHex(serverSecret, clientSecret)
    else:
        serverSecret = "X"
        randomNumber = rand256hex()
    allempty = move_logic.deserialize_board(move.allempty)
    emptyNo = len(allempty)
    board = move_logic.deserialize_board(move.board)
    position = allempty[int(randomNumber, 16)%emptyNo]
    board[position[0]][position[1]] = move_logic.new_value
    if move.moveNumber != sum(map(sum, board)):
        raise Error("moveNumber != sum(board), database corruption, we're all going to die.")
    gameover = False
    result = move.moveNumber
    game = move.belongs_to
    if emptyNo == 1:
        gameover = not move_logic.has_move(board)
        if gameover:
            result = move.moveNumber + 1
            game.result = result
            #person = game.belongs_to
            #if result > person.bestResult:
            #    person.bestResult = result
    move.board = move_logic.serialize_board(board)
    game.gameover = gameover
    game.save()
    move.save()
    return { "valid": valid,
             "serverSecret": serverSecret,
             "randomNumber": randomNumber,
             "position": position,
             "value": move_logic.new_value,
             "gameover": gameover,
             "moveNumber": result
            }