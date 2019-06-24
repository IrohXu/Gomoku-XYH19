from copy import deepcopy
import random
import pisqpipe as pp
from pisqpipe import DEBUG_EVAL, DEBUG
from board_info_helper import check_win, Adjacent, generate_board_value_lists
from CriticNetwork import CriticNetwork
from Debug import logDebug, logTraceBack
from Board import Board
import pickle
import os

MAX_BOARD = 20
WORK_FOLDER = r"F:\OneDrive\课件\人工智能\final\Gomoku-XYH19\dist/"
CRITIC_NETWORK_SAVEPATH = WORK_FOLDER+'/critic_network_new'



class ActionNetwork():
    def __init__(self, objective=1, EPSILON=0.0):
        self.objective = objective
        self.EPSILON = EPSILON
    def forward(self, board, actions, values):
        if random.random() < self.EPSILON: # EPSILON greedy
            zipped = list(filter(lambda zipped: abs(zipped[1] - self.objective)<1, zip(actions, values))) # 就算随机选也不要选必输的
            if len(zipped) > 0:
                random_index = random.randint(0, len(zipped)-1)
                logDebug("Chosen random action from %s candidates, value = %s" % (len(zipped), zipped[random_index][1]))
                return zipped[random_index][0], zipped[random_index][1]
            else:
                random_index = random.randint(0, len(actions)-1)
                logDebug("Chosen random action from %s candidates, value = %s" % (len(actions), values[random_index]))
                return actions[random_index], values[random_index]
        else:
            best_diff_from_objective = 999
            best_value = None
            best_action = None
            #logDebug('Available values: '+ str(values))
            for action, value in zip(actions, values):
                diff = abs(value - self.objective)
                if diff < best_diff_from_objective:
                    best_diff_from_objective, best_action, best_value = diff, action, value
            logDebug("Chosen best action from %s candidates, best value = %s" % (len(actions), best_value))
            return best_action, best_value



class SystemModel():
    def __init__(self, who):
        self.who = 1
    def forward(self, action):
        pp.do_mymove(action[0], action[1]) # 会更改board的值
        return board

    def forward_if(self, board, action):
        board_next = deepcopy(board)
        board_next[action[0]][action[1]] = self.who
        return board_next

class Main():
    def __init__(self, board):
        self.TRAIN = False
        self.board = board
        self.ME = 1
        self.OPPONENT = 2
        self.action_network = ActionNetwork(objective=self.ME)
        self.critic_network = CriticNetwork(params=[len(board.features)*5 + 2, 60, 1], pattern_finder=board.pattern_finder) # 神经网络结构
        if os.path.exists(CRITIC_NETWORK_SAVEPATH):
            self.critic_network.layers = pickle.load(open(CRITIC_NETWORK_SAVEPATH, 'rb'))
            logDebug('Using existing model at '+CRITIC_NETWORK_SAVEPATH)
            
        self.system_model = SystemModel(who=self.ME)
    def run_me(self):
        try:
            if board.whose_turn is None:
                board.whose_turn = self.ME

            actions, values = self.get_candidate_actions()
            action, value = self.action_network.forward(self.board, actions, values)
            board_now = deepcopy(self.board)
            board_next = self.system_model.forward(action) # pp.do_mymove here
            if self.TRAIN:
                reward = 1.0 if check_win(board_now, action[0], action[1], who=self.ME) else 0.0
                self.critic_network.back_propagation(board_now, board_next, reward)
        except:
            logTraceBack()
            raise Exception('fuck')

    def run_opponent(self, x, y):
        try:
            if board.whose_turn is None:
                board.whose_turn = self.OPPONENT

            board_now = deepcopy(self.board)
            self.board[x][y] = 2
            board_next = self.board
            reward = 0.0
            self.critic_network.back_propagation(board_now, board_next, reward)
        except:
            logTraceBack
            raise Exception('fuck')

    def get_candidate_actions(self):
        actions = Adjacent(self.board) # 返回临近的点
        values = []
        for action in actions:
            board_next = self.system_model.forward_if(self.board, action)
            values.append(self.critic_network.forward(board_next))
        return actions, values

if __name__ == '__main__':
    try:
        board = Board(MAX_BOARD)
        main = Main(board)
    except:
        logTraceBack()
        raise Exception('fuck')

    def brain_init():
        if pp.width < 5 or pp.height < 5:
            pp.pipeOut("ERROR size of the board")
            return
        if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
            pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
            return
        pp.pipeOut("OK")

    def brain_restart():
        board.reset()
        pp.pipeOut("OK")

    def isFree(x, y):
        return x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] == 0

    def brain_my(x, y):
        if isFree(x,y):
            board[x][y] = 1
        else:
            pp.pipeOut("ERROR my move [{},{}]".format(x, y))

    def brain_opponents(x, y): # 这个函数在对手胜利的那步不会被调用
        if isFree(x,y):
            main.run_opponent(x, y)
        else:
            pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))

    def brain_block(x, y):
        if isFree(x,y):
            board[x][y] = 3
            logDebug('brain_block at (%s, %s)' % (x, y))
        else:
            pp.pipeOut("ERROR winning move [{},{}]".format(x, y))

    def brain_takeback(x, y):
        if x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] != 0:
            board[x][y] = 0
            return 0
        return 2

    def brain_turn():
        if pp.terminateAI:
            logDebug('terminateAI')
            return
        main.run_me()

    def brain_end():
        try:
            pickle.dump(main.critic_network.layers, open(CRITIC_NETWORK_SAVEPATH, 'wb'))
        except:
            logTraceBack()
            raise Exception('fuck')
        

    def brain_about():
        pp.pipeOut('fuck')

    pp.brain_init = brain_init
    pp.brain_restart = brain_restart
    pp.brain_my = brain_my
    pp.brain_opponents = brain_opponents
    pp.brain_block = brain_block
    pp.brain_takeback = brain_takeback
    pp.brain_turn = brain_turn
    pp.brain_end = brain_end
    pp.brain_about = brain_about


    pp.main()



