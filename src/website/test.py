#Copyright (c) Adam Kurkiewicz 2014, all rights reserved.
import move_logic
board = [[1,0,1,3], [0, 1, 2, 3], [0, 0, 1, 2], [2, 0, 3 ,0]]
move_logic.pretty_board(board)
result = move_logic.next_board(board, True, False)
move_logic.pretty_board(result["newboard"])
print result

