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
from queries import *

def index(request):
    useragent = request.META['HTTP_USER_AGENT']
    goodBrowsers = ["Opera", "Lunascape", "Sleipnir"]
    isNice = any([good in useragent for good in goodBrowsers])
    if "MSIE" in useragent and not isNice:
        return render(request, "IEHate.html", {})
    return processAndRender(request, 'main.html')

def play(request):
    return processAndRender(request, 'play.html')

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
    previous_move = game.lastMove
    previous_board = move_logic.deserialize_board(previous_move.board)
    full_board = move_logic.next_board(previous_board, *booleans)
    board = full_board["newboard"]
    allempty = full_board["allempty"]
    changed = full_board["changed"]
    if changed:
        try:
            current_move = negotiate_first(game, board, allempty, request.POST["clientSecretHashed"])
        except UnfinishedMove:
            return HttpResponse("Pacta sunt servanda. You are obliged to finish " +
                                "your previous move by exchanging secrets. To " +
                                "give up the negotiation and accept server's" +
                                "choice of the pseudorandom number send" + 
                                '"surrender="True""', status=452)
    else:
        current_move = previous_move
    full_board["serverSecretHashed"] = current_move.serverSecretHashed;
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
        return HttpResponse("Pacta sunt servanda. You should start the movement\
by declaring your commitment first", status=452)

    if surrender == "True":
        response = {
            "valid": True,
            "serverSecret": "",
            "randomNumber": rand256hex(),
            "position": None,
            "value": 1
        }
    else:
        response = check_validity(move)
    return HttpResponse(json.dumps(response),
                        content_type='application/json')