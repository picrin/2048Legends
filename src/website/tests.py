from django.test import TestCase
#from myapp.models import Animal
import move_logic as mv
import datetime
import logic_glue
import hashlib
from models import Person, Tokena, Game, Move
from django.test.client import RequestFactory
from logic_glue import *
import views

class Bleh(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.board = mv.create_board
    def test_moves(self):
        board = mv.create_board(4)
        board[1][1] = 2
        board[1][3] = 2
        board[2][2] = 2
        board[3][1] = 2
        newboard = mv.next_board(board, False, False)["newboard"]
        self.assertEqual(newboard[1][0], 4)
        self.assertEqual(newboard[2][0], 2)
        self.assertEqual(newboard[3][0], 2)
    #TODO test moves in other directions as well.
    def test_protocol(self):
        #Assume one user logged in in one place with one non-gameovered game.
        examplePerson = Person(login="picrin", hashedPassword="1")
        examplePerson.save()
        token = Tokena(value="letmein", active=True, created=datetime.datetime.utcnow(), belongs_to=examplePerson)
        token.save()
        game = views.newGame(examplePerson)
        examplePerson.currentGame = game
        #Assume that person issues new game request. Assume following data
        #secret: f5acc1629ccc8ce5a32eb3f2b405adc85a265e231912957b2714aa756f7e140d
        #hashedSecret: 68798143dd5a01b94d254f52cb54fa6fbbe031d3d216fc161979e7c6c92fcee4
        request = self.factory.post('/nextmove',
                {
                "clientSecretHashed" : "68798143dd5a01b94d254f52cb54fa6fbbe031d3d216fc161979e7c6c92fcee4",
                "direction": "up"
                })
        clientSecretHashed = str(request.POST["clientSecretHashed"])
        request.COOKIES["tokena"] = "letmein"
        username = token_to_username(request)
        self.assertEqual(username, "picrin")
        board = mv.create_board(4)
        board[2][2] = 2
        resolved_board = mv.next_board(board, True, False)["newboard"]
        negotiate_first(game, resolved_board, clientSecretHashed)
        
        #clientSecret = str(request.POST["clientSecret"])

