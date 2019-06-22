from Board import Board
import time

board_class = Board(20)
board_list = [[0 for j in range(20)] for i in range(20)]

steps = [
    [10,10],
    [11,10],
  [10,11],
  [10,9],  
  [9,11],  
  [12,11],  
  [9,8],  
  [13,12],  
  [14,13],  
  [11,9],  
 [8,11],  
 [11,11],  
 [11,12],  
 [11,8],  
 [11,7],  
 [12,9],  
 [9,9],  
 [13,9],  
 [14,9],  
 [12,10],  
 [9,10],  
 [8,7],  
 [9,7],  
]

start = time.time()
for i in range(100):
    for j, step in enumerate(steps):
        whose_turn = 1 if j%2==0 else 2
        board_class[step[0]][step[1]] = whose_turn
print('Board Class took %s seconds'%(time.time()-start))


start = time.time()
for i in range(100):
    for j, step in enumerate(steps):
        whose_turn = 1 if j%2==0 else 2
        board_list[step[0]][step[1]] = whose_turn
print('Board List took %s seconds'%(time.time()-start))