#Copyright (c) Adam Kurkiewicz 2014, all rights reserved.
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
from logic_glue import *

def index(request):
    useragent = request.META['HTTP_USER_AGENT']
    goodBrowsers = ["Opera", "Lunascape", "Sleipnir"]
    isNice = any([good in useragent for good in goodBrowsers])
    if "MSIE" in useragent and not isNice:
        return render(request, "IEHate.html", {})
    return processAndRender(request, 'main.html')

def play(request):
    return processAndRender(request, 'play.html')

def newGame(user):
    board = move_logic.create_board(move_logic.size)
    board[1][1] = 1
    move = Move(
            belongs_to = None,
            moveNumber = 0,
            board = move_logic.serialize_board(board),
            serverSecret = "0",
            serverSecretHashed = "0",
            clientSecret = "0",
            clientSecretHashed = "0"
            )
    move.save()
    game = Game(
            belongs_to = user,
            gameover = False,
            lastMove = move
            )
    game.save()
    move.belongs_to = game
    move.save()
    return game
    
def get_board(request):
    resp = {}
    user = token_to_user(request)
    if user is not None:
        game = user.currentGame
        if game is None or game.gameover:
            game = newGame(user)
            user.currentGame = game
            user.save()
    else:
        #TODO provide some persistence for unlogged users.
        game = newGame(None)
    resp["board"] = move_logic.deserialize_board(game.lastMove.board)
    return HttpResponse(json.dumps(resp), content_type='application/json')

def login(request):
    return processAndRender(request, "login.html")

def logout(request):
    retrieve_token(request, delete = True)
    response = render(request, 'main.html')
    response.delete_cookie('tokena')
    return response

def get_user(request, delete_token = False):
    username = token_to_username(request)
    if username is not None:
        return HttpResponse(username, RequestContext(request), status=200)
    else:
        return HttpResponse("not logged in/ invalid token.", status=404)
    


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
    return processAndRender(request, "register.html")

def exchangeCommitments(request):
    #tokena = request.POST["tokena"]
    #get_user from tokena 
    #retrive user's latest game
    #check that it is not gameovered, return "403 grab a new board" on error
    #retrive user's latest move
    #check that it's not unfinished, i.e. look at clientSecret not empty, return 403 "pacta sunt servanda" on error. If client can't complete the move for whatever reason, second step of the move should allow passing an empty string to agree for any random number
    #game = Game.objects
    #game = game.filter(gameover = False)
    #userid = 
    #game = game.belongs_to()
    #token = Tokena.objects
    #token = token.filter(value=cookie)
    #token = token.filter(active=True)
    #print board
    
    #TODO 1)
    
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
    user = token_to_user(request)
    game = user.currentGame
    move = game.lastMove
    previous_board = move_logic.deserialize_board(move.board)
    full_board = move_logic.next_board(previous_board, *booleans)
    board = full_board["newboard"]
    try:
        negotiate_first(game, board, request.POST["clientSecretHashed"])
    except UnfinishedMove:
        return HttpResponse("Pacta sunt servanda. You are obliged to finish " +
                            "your previous move by exchanging secrets. To " +
                            "give up the negotiation and accept server's" +
                            "choice of the pseudorandom number send" + 
                            'surrender="True"', status=452)
    #serverSecretHashed = negotiate_first(request)
    #full_board["serverSecretHashed"] = serverSecretHashed;
    return HttpResponse(json.dumps(full_board),
                        content_type='application/json')

def exchangeSecrets(request):
    surrender = request.POST["surrender"]
    clientSecret = request.POST["clientSecret"]
    user = token_to_user(request)
    game = user.currentGame
    move = game.lastMove

    try:
        negotiate_second(game, clientSecret)
    except UnfinishedMove:
        return HttpResponse("Pacta sunt servanda. You should start the movement by declaring your commitment first", status=452)

    if surrender == "True":
        response = {
            "valid": True,
            "serverSecret": "",
            "randomNumber": rand256hex(),
            "position": 4,
            "value": 1
        }
    else:
        response = check_validity(move)
    return HttpResponse(json.dumps(response),
                        content_type='application/json')