from Board import Board
from Resource import RESOURCE_DIR
from CriticNetwork import CriticNetwork
import os
import pickle

MAX_BOARD = 20
board = Board(MAX_BOARD)

CRITIC_NETWORK_SAVEPATH = RESOURCE_DIR + '/critic_network_nnew'
critic_network = CriticNetwork(params=[len(board.features)*5 + 2, 60, 1], pattern_finder=board.pattern_finder)
if os.path.exists(CRITIC_NETWORK_SAVEPATH):
    critic_network.layers = pickle.load(open(CRITIC_NETWORK_SAVEPATH, 'rb'))
    print('Using existing model at '+CRITIC_NETWORK_SAVEPATH)

board.load('history5.txt', 2)
board.print()
print(critic_network.forward(board))

board[13][7] = 1
board.print()
print(critic_network.forward(board))
'''
board[11][10] = 2
board.print()
print(critic_network.forward(board))
'''