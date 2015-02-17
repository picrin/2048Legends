import move_logic as _2048
board = _2048.create_board()
_2048.inject_random(board)
_2048.inject_random(board)
with open("output", 'w') as fifo:
    fifo.write(str(board))
    fifo.write("\n")
_2048.pretty_board(board)
moves = 0
while True:
    updown = False
    downright = False
    with open("input", 'r') as fifo:
        command = fifo.readline()[:-1]
        if command == "left":
            pass
        elif command == "right":
            downright = True
        elif command == "down":
            downright = True
            updown = True
        elif command == "up":
            updown = True
        else:
            continue
    board = _2048.next_board(board, updown, downright)
    _2048.inject_random(board)
    moves += 1
    with open("output", 'w') as fifo:
        fifo.write(str(board))
        fifo.write("\n")
    _2048.pretty_board(board)

