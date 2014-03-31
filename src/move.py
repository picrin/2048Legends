class _Getch:
    """Gets a single character from standard input.  Does not echo to the screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()
class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

import os

size = 4

def create_board(size):
    return [[0 for i in range(size)] for ii in range(size)]

def if_invert(iterable, invert = False):
    if invert:
        return iterable[::-1]
    else:
        return iterable

def new_coordinate(constant, inaxis, move_by, updown, downright):
    if downright:
        by = 1
    else:
        by = -1
    return if_invert((constant, move_by * by + inaxis), updown)

def next_board(board, updown, downright):
    all_moves = {}
    for x in if_invert(range(size), updown):
        merge_possible = True
        move_by = 0
        previous_value = None
        for y in if_invert(range(size), downright):
            index = if_invert((x, y), updown)
            value = board[index[0]][index[1]]
            if value != 0:
                if merge_possible:
                    if previous_value == value:
                        move_by += 1
                        merge_possible = False
                else:
                    merge_possible = True
                previous_value = value
                if move_by != 0:
                    nc = new_coordinate(x, y, move_by, updown, downright)
                    all_moves.setdefault(index[0], {})[index[1]] = nc
            else:
                move_by += 1

    newboard = [[xy for xy in row ] for row in board]

    for xs in all_moves:
        for ys in all_moves[xs]:
            pos = all_moves[xs][ys]
            newboard[pos[0]][pos[1]] += board[xs][ys]
            newboard[xs][ys] -= board[xs][ys]
            

    all_empty = []
    for x, lista in enumerate(newboard):
        for y, elem in enumerate(lista):
            if elem == 0:
                all_empty.append((x, y))
    newpos = None
    #TODO work on this
    if len(all_moves) != 0 and len(all_empty) != 0:
            newpos = all_empty[int(os.urandom(1).encode("hex"), 16)%len(all_empty)]
            newboard[newpos[0]][newpos[1]] = 2
    else:
        if not has_move(board):
            print "game over"
        else:
            pass
        
    return newboard, all_moves, newpos

def pretty_board(board):
    for x in board:
        print
        for y in x:
            print y,
    print

getch = _Getch()

currentboard = create_board(4)
currentboard[0][1] = 2
booleans = (True, True)
while True:
    currentboard = next_board(currentboard, *booleans)[0]
    pretty_board(currentboard)
    char = getch()
    if char == 's':
        booleans = (True, True)        
    elif char == 'w':
        booleans = (True, False)        
    elif char == 'a':
        booleans = (False, False)        
    elif char == 'd':
        booleans = (False, True)        
    else:
        break

"""
board = create_board(size)
#16 4 2 0
#8 4 0 0
#4 0 0 0
#2 0 0 0

board[0][0] = 16
board[0][1] = 4
board[0][2] = 2
board[0][3] = 0

board[1][0] = 8
board[1][1] = 4
board[1][2] = 0
board[1][3] = 0

board[2][0] = 4
board[2][1] = 0
board[2][2] = 0
board[2][3] = 0

board[3][0] = 2
board[3][1] = 0
board[3][2] = 0
board[3][3] = 0

pretty_board(board)
pretty_board(next_board(board, False, True)[0])
"""
