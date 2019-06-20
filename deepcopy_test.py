from Board import Board
from copy import deepcopy
import time

board = Board(20)

start = time.time()
for _ in range(100):
    b = deepcopy(board)
print('Original deepcopy: %s'% (time.time()-start))

start = time.time()
for _ in range(100):
    b = board.deepcopy()
print('Revised deepcopy: %s'% (time.time()-start))
