from board_info_helper import *
from Board import Board

MAX_BOARD = 20
board = Board(MAX_BOARD)

board.load('history5.txt', 2)
board.print()

board[7][10] = 2
who = 2
print(count_live_three_my(board, 2) + count_rest_four_my(board, 2))
print(count_rest_three_op(board, who)+count_live_three_op(board, who))

        
