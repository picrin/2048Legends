#Copyright (c) Adam Kurkiewicz 2014, all rights reserved.
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

def pretty_board(board):
    for row in board:
        print
        for elem in row:
            print elem,
    print

def resolve_moves(board, newboard, moves):
    for row in moves:
        for col in moves[row]:
            pos = moves[row][col]
            newboard[pos[0]][pos[1]] += board[row][col]
            newboard[row][col] -= board[row][col]

def all_empty(board):
    allempty = []
    for x, lista in enumerate(board):
        for y, elem in enumerate(lista):
            if elem == 0:
                allempty.append((x, y))
    return allempty

#def count_non_empty(board):
#    non_empty = 0
#    for x, lista in enumerate(board):
#        for y, elem in enumerate(lista):
#            if elem != 0:
#                non_empty += 1
#    return non_empty

def generate_moves(moves):
    for x in moves:
        for y in moves[x]:
            yield x, y


def next_board(board, updown, downright):
    clear_moves = {}
    merge_moves = {}
    all_moves = {}
    for row in if_invert(range(size), updown):
        merge_possible = True
        move_by = 0
        previous_value = None
        report_to = clear_moves
        for col in if_invert(range(size), downright):
            index = if_invert((row, col), updown)
            value = board[index[0]][index[1]]
            if value != 0:
                if merge_possible:
                    if previous_value == value:
                        move_by += 1
                        merge_possible = False
                        report_to = merge_moves
                else:
                    merge_possible = True
                    report_to = clear_moves
                previous_value = value
                #that could be perhaps modified to include logic for
                #static_moves as well.
                if move_by != 0:
                    nc = new_coordinate(row, col, move_by, updown, downright)
                    for moves in [report_to, all_moves]:
                        moves.setdefault(index[0], {})[index[1]] = nc
            else:
                move_by += 1

    newboard = [[element for element in row] for row in board]
    resolve_moves(board, newboard, all_moves)
    all_fields  = ((x, y) for x in range(size) for y in range(size))
    static_moves = [(x, y) for (x, y) in all_fields if (x, y) not in generate_moves(all_moves) and board[x][y] != 0]
    
    allempty = all_empty(newboard)
    print allempty
    newpos = None
    if len(all_moves) != 0 and len(allempty) != 0:
        #TODO extract method
        newpos = allempty[int(os.urandom(1).encode("hex"), 16)%len(allempty)]
        newboard[newpos[0]][newpos[1]] = 2

    else:
        #TODO finish the pseudocode
        #if not has_move(board):
        #    return gameon: False
        #else:
        #    pass
        pass
    results = {
            "oldboard": board,
            "clear_moves": clear_moves,
            "merge_moves": merge_moves,
            "all_empty" : allempty,
            "static_moves": static_moves,
            "newpos": newpos,
            "newboard": newboard,
            "gameon": True,
            }

    #Speaking of moves, we return row number first, later column number.
    #This might seem strange, but it's natural once you
    #look at our representation: we have 4 small tables
    #of rows in a bigger table. So think rows/colums, not x/y
    return results
