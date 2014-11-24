#Copyright (c) Adam Kurkiewicz 2014, all rights reserved.
from WC2048 import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from django.http import Http404, HttpResponseServerError, HttpResponseForbidden
from django.utils.http import urlquote
from models import Person, Transaction, Tokena, Game, Move
import move_logic
import datetime
import hmac
import hashlib
import binascii
import re
import string
import urllib2
import json
from queries import *


#checks that the callback contains all of the required fields
def validate_callback(get_response):
    return (True, "No error.")

#Called by bc info when we recieve a payment. we must do the following things:
#   # check the input address against all of the transactions to find which one it matches
#   # confirm that the destination address matches our bitcoin address
#   # convert the value in to bitcoins
#   # find out how many games they can get for this amount
#   # get the person from the transaction.
#   # update the person's play count with their new total plays
#   # update the transaction information
#   # respond with an "*ok*"

def bitcointestcallback(request):
    is_valid, error_message = validate_callback(request.GET)
    if not is_valid:
        print "RECIEVED A MALFORMED/ILLEGAL CALLBACK. Error message:", error_message, "\n\n", request.GET
        return HttpResponse("*ok*")
    
    input_address = request.GET.get("input_address")
    destination_address = request.GET.get("destination_address")
    transaction_secret = request.GET.get("secret")
    value = request.GET.get("value")
    value = float(value)/100000000.0 #changing value from satoshi to bitcoin
    
    print "RECIEVED CALLBACK", input_address, transaction_secret, value 
    
    #checking that the destination address matches ours.
    if destination_address != OUR_WALLET:
        print "ERROR: destination address", destination_address, " does not match OUR_WALLET address."
        return HttpResponse("*ok*")
    
    #finding the transaction in the database for this payment
    try:
        transaction = Transaction.objects.get(wallet_id=input_address)
    except Transaction.DoesNotExist:
        print "ERROR: matching transaction cannot be found in database for input_address", input_address
        return HttpResponse("*ok*")
    
    #checking that the secret key in the transaction and callback match
    if transaction_secret != transaction.transaction_secret:
        print "ERROR: transaction_secret", transaction_secret, " does not match the one stored in the database:", transaction.transaction_secret
        return HttpResponse("*ok*")
        
    #checking that the transaction has not already been completed
    if transaction.is_completed():
        print "ERROR: transaction with input_address", transaction.wallet_id, " has already been completed."
        return HttpResponse("*ok*")
    
    #checking that the value is a valid amount and matches the transaction
    if value < GAME_COST:
        print "ERROR: transaction's value", value, " is not a valid amount."
        return HttpResponse("*ok*")
        
    if value != transaction.intended_currency:
        print "WARNING: transaction's value", value, " does not match the intended value of", transaction.intended_currency, ". The user will recieve as many plays as they are able to afford with aforementioned amount."
    
    #finding out how many games the bitcoins can buy.
    plays = int(value/GAME_COST)
    
    #getting the person from the transaction and updating their play count with the new amount of games.
    person = transaction.belongs_to
    print person.login, "with current balance", person.gamesRemaining, "will be given", plays
    
    person.gamesRemaining = person.gamesRemaining + plays
    person.save()
    
    print person.login, "new balance", person.gamesRemaining
    
    #updating the transaction to say it has been completed.
    transaction.recieved_currency = value
    transaction.recieved_plays = plays
    transaction.date_completed = datetime.now()
    transaction.save()
    
    return HttpResponse("*ok*")


#checks that the intended amount of games bought and the cost are valid.
#returns a tuple with the validation success, and an error message.
def validate_buy(intended_games, intended_cost, person):
    if intended_games is None or intended_cost is None:
        return (False, "The intended games or intended cost were not specified!")
    if person == None:
        return (False, "There was an error identifying your user. You must be logged in to buy games!")
        
    return (True, "No error.")


#gets a new input address from bc info and returns it. takes a transaction_secret to put in the callback url
def get_new_input_address(transaction_secret):
    global OUR_WALLET, OUR_URL
    
    callback_url = urlquote('http://' + OUR_URL + '/bitcointestcallback?secret=' + transaction_secret)
    url =   'http://www.blockchain.info/api/receive?method=create&cors=true&format=plain&address='+ OUR_WALLET + '&shared=false&callback=' + callback_url
    
    return_data = urllib2.urlopen(url).read()
    data = json.loads(return_data)
    print data
    
    return data.get('input_address')
    
# Called when the person clicks a button to set up a transaction and return them a wallet id.
#
# get intended games and cost, and validate
# generate a transaction secret
# generate callback address
# request a new wallet id from blockchain.info
# create new transaction object with a belongs_to, wallet id, secret, intended plays, intended currency
# add transaction object to database
# send back the wallet id for user and the cost
#
# we should recieve the person buying, the number of games to buy, and the expected cost.
# We send the wallet id to be displayed to the user.
# NOTE - WHILE TESTING WE DON'T HAVE LOGINS WORKING, SO WE ALWAYS FETCH THE SAME PERSON.
def buybuttonclick(request):
    #getting the plays and cost from the get request
    intended_plays = request.GET.get('intended_plays')
    intended_currency = request.GET.get('intended_currency')
    
    #finding the person who is issuing the buy request
    person = Person.objects.all()[0] #token_to_user(request)
    
    #validating this request
    is_valid, error_message = validate_buy(intended_plays, intended_currency, person)
    
    #setting up the return_information json dict and getting a wallet id if valid.
    return_information = {'error':not is_valid, 'error_message':error_message, 'currency':intended_currency}
    if is_valid:
        #generating a transaction secret to embed in out callback address.
        #then calling bc info with the transaction secret and getting a wallet address.
        transaction_secret = Transaction.generate_secret()
        input_address = get_new_input_address(transaction_secret)
    
        #creating the transaction database entry and saving it to the database.
        transaction =   Transaction(belongs_to=person, wallet_id=input_address, \
                        transaction_secret=transaction_secret, intended_plays=intended_plays, \
                        intended_currency=intended_currency)
        transaction.save()
        
        #setting the walled id for the return information
        return_information['wallet_id'] = input_address
    else:
        #since thr data was invalid, we did not generate a wallet id. hence, walled_id=none
        return_information['wallet_id'] = 'None'
    
    #returning the json to the client whose javascript will parse it.
    return HttpResponse(json.dumps(return_information))
    
    
    

def index(request):
    useragent = request.META['HTTP_USER_AGENT']
    goodBrowsers = ["Opera", "Lunascape", "Sleipnir"]
    isNice = any([good in useragent for good in goodBrowsers])
    if "MSIE" in useragent and not isNice:
        return render(request, "IEHate.html", {})
    return processAndRender(request, 'main.html')

def play(request):
    return processAndRender(request, 'play.html', templateVars={"active_play": True})
    #return HttpResponse(str(Game.objects.all()[0].lastMove.board))
    
def buy(request):
    return processAndRender(request, 'buy.html', templateVars={'PRICE_PER_GAME':settings.GAME_COST})
    #return HttpResponse(str(Game.objects.all()[0].lastMove.board))

def user(request):
    print(dir(request))
    username = request.path.split("/")[-1]
    people = Person.objects.filter(login = username)
    if not people:
        raise Http404()
    templateVars = {"results": genPersonal(people[0]), "transactions":genTransactions(people[0]), "username": username}
    return processAndRender(request, "user.html", templateVars)

def genPersonal(person):
    return [game.result for game in Game.objects.filter(belongs_to=person).order_by("-result") if game.result is not None]
    
def genTransactions(person):
    return [transaction for transaction in person.transaction_set.order_by("-date_created")]

def genLeaders():
    for game in Game.objects.all().order_by('-result'):
        user = game.belongs_to
        result = game.result
        if user is None:
            username = "anonymous"
        else:
            username = user.login
        if result is not None:
            yield str(username), game.result

def leaderboard(request):
    return processAndRender(request, "leaderboard.html", templateVars={"active_leaderboard": True, "results":list(genLeaders())})

def get_board(request):
    resp = {}
    user = token_to_user(request)
    #for unlogged users
    hasGameID = "gameid" in request.COOKIES
    setGameID = False
    if user is not None:
        game = user.currentGame
        if game is None:
            game = newGame(user)
            user.currentGame = game
            user.save()
    elif hasGameID:
        game = cookie_to_game(request)
        if game is None:
            game = newGame(user)
            setGameID = True
    else:
        game = newGame(None)
        setGameID = True
    if game.gameover:
        game = newGame(user)
        setGameID = True
    if user is not None:
        user.currentGame = game
        user.save()
    
    resp["board"] = move_logic.deserialize_board(game.lastMove.board)
    resp["moveNumber"] = game.lastMove.moveNumber
    response = HttpResponse(json.dumps(resp), content_type='application/json')
    if setGameID:
        response.set_cookie("gameid", value=game.gameid, httponly=False)
    return response
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

def register(request):
    return processAndRender(request, "register.html")

import time
import thread
userlocks = {}
def callSingle(user, callback, argsTuple):
    if user is None:
        return callback(*argsTuple), True
    lock = userlocks.setdefault(user.login, thread.allocate_lock())
    allowed_in = lock.acquire_lock(False)
    fail_response = HttpResponse("I'm doing a database operation for you. It's a difficult and delicate process. I need to focus. Alone. Do not disturb.", status=420)
    if allowed_in:
        try:
            return callback(*argsTuple), True
        except Exception as e:
            fail_response, False
        finally:
            lock.release()
    else:
        return fail_response, False

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
    user, game = token_to_game(request)
    return callSingle(user, prepareCommitment, (game, booleans, request.POST["clientSecretHashed"]))[0]

def prepareCommitment(game, booleans, clientCommitment):
    previous_move = game.lastMove
    previous_board = move_logic.deserialize_board(previous_move.board)
    full_board = move_logic.next_board(previous_board, *booleans)
    board = full_board["newboard"]
    allempty = full_board["allempty"]
    changed = full_board["changed"]
    if changed:
        try:
            current_move = negotiate_first(game, board, allempty, clientCommitment)
        except UnfinishedMove:
            return HttpResponse("Pacta sunt servanda. You are obliged to finish " +
                                "your previous move by exchanging secrets. To " +
                                "give up the negotiation and accept server's" +
                                "choice of the pseudorandom number send" + 
                                '"surrender="True""', status=452)
    else:
        return HttpResponseForbidden("not changed!")
        
    full_board["serverSecretHashed"] = current_move.serverSecretHashed;
    full_board["moveNumber"] = current_move.moveNumber
    return HttpResponse(json.dumps(full_board),
                        content_type='application/json')

def exchangeSecrets(request):
    surrender = request.POST["surrender"]
    clientSecret = request.POST["clientSecret"]
    user, game = token_to_game(request)
    try:
        response, worked = callSingle(user, negotiate_second, (game, clientSecret))
    except UnfinishedMove:
        return HttpResponse("Pacta sunt servanda. You should start the movement\
by declaring your commitment first", status=452)
    if worked:
        return HttpResponse(json.dumps(response), content_type='application/json')
    else:
        response