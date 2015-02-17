#Copyright (c) Adam Kurkiewicz 2014, all rights reserved.
import os
import json
size = 4
new_value = 1
def create_board():
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

def generate_moves(moves):
    for x in moves:
        for y in moves[x]:
            yield x, y

def serialize_board(board):
    return json.dumps(board)
    
def deserialize_board(board_string):
    return json.loads(board_string)

def has_move(board):
    for rowNo in range(size - 1):
        for colNo in range(size):
            if board[rowNo][colNo] == board[rowNo + 1][colNo]:
                return True
    for rowNo in range(size):
        for colNo in range(size - 1):
            if board[rowNo][colNo] == board[rowNo][colNo + 1]:
                return True
    return False

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
    print all_moves
    return newboard
import random
random.random = None
randr = random.SystemRandom()
def inject_random(board):
    new_2 = randr.choice(all_empty(board))
    board[new_2[0]][new_2[1]] = 2
