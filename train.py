import adp
from adp import CriticNetwork, Board, ActionNetwork
from copy import deepcopy
from board_info_helper import Adjacent
import os
import pickle
import random
import Debug

Debug.LOG_MODE = 'FUCK'
WORK_FOLDER = r"F:\OneDrive\课件\人工智能\final\Gomoku-XYH19/train"
CRITIC_NETWORK_SAVEPATH = WORK_FOLDER+'/critic_network'

ME = 1
OPPONENT = 2
OBJECTIVE_MY = 1
OBJECTIVE_OPPONENTS = 0
MAX_BOARD = 20

adp.board = Board(MAX_BOARD)
board = adp.board

action_network_me = ActionNetwork(objective=OBJECTIVE_MY, EPSILON=0.01)
action_network_opponent = ActionNetwork(objective=OBJECTIVE_OPPONENTS, EPSILON=0.01)

critic_network = CriticNetwork(params=[len(board.features)*5 + 2, 60, 1], pattern_finder=board.pattern_finder) # 神经网络结构
if os.path.exists(CRITIC_NETWORK_SAVEPATH):
    critic_network.layers = pickle.load(open(CRITIC_NETWORK_SAVEPATH, 'rb'))
    adp.logDebug('Using existing model at '+CRITIC_NETWORK_SAVEPATH)

def get_candidate_actions(who):
    actions = Adjacent(board) # 返回临近的点
    values = []
    for action in actions:
        x, y = action
        board_next = board.deepcopy()
        board_next[x][y] = who
        values.append(critic_network.forward(board_next))
    return actions, values


win_record = []
for i in range(2000):
    while board.win is None:
        if board.whose_turn is None:
            board.whose_turn = random.choice([ME, OPPONENT])

        if board.whose_turn == ME:
            print('MY TURN:')
            actions, values = get_candidate_actions(ME)
            action, value = action_network_me.forward(board, actions, values)
            board_now = deepcopy(board)
            board[action[0]][action[1]] = ME # pp.do_mymove here
            reward = 1.0 if (board.win is not None and board.win) else 0.0
            critic_network.back_propagation(board_now, board, reward)
        else:
            print('OPPONENT\'S TURN:')
            actions, values = get_candidate_actions(OPPONENT)
            action, value = action_network_opponent.forward(board, actions, values)
            board_now = deepcopy(board)
            board[action[0]][action[1]] = OPPONENT # pp.do_mymove here
            reward = 0.0
            critic_network.back_propagation(board_now, board, reward)

    print('Game %s set. Winner: ' % i+ ('ME' if board.win else 'OPPONENT') )
    win_record.append('ME' if board.win else 'OPPONENT')
    try:
        with open(CRITIC_NETWORK_SAVEPATH, 'wb') as f:
            pickle.dump(critic_network.layers, f)
            f.close()
    except:
        print('Save model failed')
    board.reset()

print('Win record: '+ str(win_record))