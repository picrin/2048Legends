from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from django.http import Http404
from django.utils import simplejson

import move_logic

board = None
def index(request):
    return render(request, 'main.html', RequestContext(request))

def play(request):
    global board
    return render(request, 'play.html', RequestContext(request))

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
    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')    

def nextmove(request):
    global board    
    direction = request.POST["direction"]

    if direction == '1':
        booleans = (False, True)
    elif direction == '2':
        booleans = (True, True)        
    elif direction == '0':
        booleans = (True, False)        
    elif direction == '3':
        booleans = (False, False)        
    else:
        raise Http404
    full_board = move_logic.next_board(board, *booleans)
    board = full_board[0]    
    move_logic.pretty_board(full_board[0])
    resp = {}
    resp["moves"] = full_board[1]
    resp = simplejson.dumps(resp)
    return HttpResponse(resp, mimetype='application/json')

