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
    """
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
    """
    #sometimes game over triggers too early. Especially when allempty = [[3, 3]] and [3, 2] is 1
    def gameover(self):
        board = [[128, 64, 32, 16], [64, 32, 16, 8], [32, 16, 8, 4], [16, 8, 1, 0]]
        boardString = move_logic.serialize_board(board)
        allempty = [[3, 3]]
        allemptyString = move_logic.serialize_board(allempty)
        move = Move(
                belongs_to         = None,
                moveNumber         = 100,
                board              = boardString,
                allempty           = allemptyString,
                serverSecret       = "a04aa4256d3fb3847c9a594975fd26efbdebac31bd17b88b0b39be592567230b",
                serverSecretHashed = "aa1e27d29a4e17d308534ceb6c2774d9ec4f2b9ef1022a49d66a3770ca424a13",
                clientSecret       = "",
                clientSecretHashed = "fee9aa280f017fd716c496afe03a6291bf9a0fe80f07a9026efc4257b71fe848",
                )
        move.save()
        game = Game(
                belongs_to = None,
                lastMove   = move,
                gameover   = False,
                result     = None,
                gameid     = "jakasgra"
                )
        game.save()
        move.belongs_to = game
        move.save()
        returned = negotiate_second(game, "b7d64a5f92b663560a3f000a947fae7cad549a5c2e396a4828c5151fd5034ce4")
        self.assertEqual(returned["valid"], True)
        self.assertEqual(returned["gameover"], False)


