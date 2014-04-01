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
    for x in board:
        print
        for y in x:
            print y,
    print

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
        #if not has_move(board):
        #    print "game over"
        #else:
        #    pass
        pass
    return newboard, all_moves, newpos
