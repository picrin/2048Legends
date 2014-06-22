#Copyright (c) Adam Kurkiewicz 2014, all rights reserved.
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

#def test(request):
#    board = [[1, 0, 1, 3], [0, 1, 2, 3], [0, 0, 1, 2], [2, 0, 3 ,0]]
#    move_logic.pretty_board(board)
#    result = move_logic.next_board(board, True, False)
#    move_logic.pretty_board(result["newboard"])
#    return HttpResponse(simplejson.dumps(result), mimetype='application/json')


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
    return HttpResponse(simplejson.dumps(full_board), mimetype='application/json')

