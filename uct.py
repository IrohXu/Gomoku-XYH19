import random
import time
import copy
import sys
import pisqpipe as pp
import math
from pisqpipe import DEBUG_EVAL, DEBUG
import Debug
Debug.DEBUG_LOGFILE = 'uctlog'

logDebug = Debug.logDebug
logTraceBack = Debug.logTraceBack

from Board import Board
from CriticNetwork import CriticNetwork
import pickle
import os
from Resource import RESOURCE_DIR
from board_info_helper import Adjacent




class Node():
    def __init__(self, action, parent, board=None):
        where, who = action

        self.action = action
        self.children_expanded = {}
        self.successors = None
        self.parent = parent
        self.N = 0.0
        self.Q = 0.0

        if parent is not None:
            new_board = parent.board.deepcopy()
            new_board[where[0]][where[1]] = who
            self.board = new_board
        else: # parent is None
            self.board = board
            self.action = (None, 1 if board.whose_turn==2 else 2)

    def where(self):
        return self.action[0]

    def who(self):
        return self.action[1]

    def uct_value(self):
        '''UCT价值公式'''
        return self.Q/self.N + 0.1*math.sqrt(2*math.log(self.parent.N)/self.N) # 对自己的simulation有信心的话就把探索系数设小一点
    
    def win_rate(self):
        return self.Q/self.N

    def best_successor_to_explore(self):
        '''根据UCT的价值公式选出最有价值的子节点'''
        action, node = max(
                                ( item for item in list(self.children_expanded.items()) ), 
                                key=lambda item: item[1].uct_value() # action=item[0], node=item[1]
                            )
        return node
    
    def best_successor_to_take(self):
        '''根据胜率选出最有价值的子节点'''
        action, node = max(
                                ( item for item in list(self.children_expanded.items()) ), 
                                key=lambda item: item[1].win_rate() # action=item[0], node=item[1]
                            )
        return node

    def get_successors(self):
        if self.successors is None:
            adjacents = Adjacent(self.board, shuffle=False)
            assert self.board.whose_turn != self.who()
            self.successors = list(map(lambda where:(where, self.board.whose_turn), adjacents))
        return self.successors
    
    def is_terminal(self):
        return self.board.win is not None
    
    def is_expandable(self):
        return len(self.children_expanded) < len(self.get_successors())

class UCT(object):
    def __init__(self, board, eval_function):
        '''
        Args:
            board: Board类
            eval_function: simulation达到MAX_DEPTH后使用的评估函数，输入为Board类，输出为0到1之间的浮点数
        '''
        self.initial_board = board
        self.root = Node(action=(None, None), parent=None, board=board)
        self.eval_function = eval_function
        self.MAX_DEPTH = 4
        self.DECAY = 0.9

    def reset(self):
        self.root = Node(action=(None, None), parent=None, board=board)

    def select(self):
        v = self.root
        while not v.is_terminal():
            if v.is_expandable():
                return self.expand(v)
            else:
                v = v.best_successor_to_explore()
        return v
    
    def expand(self, v):
        for action in v.get_successors():
            if action not in v.children_expanded: 
                node = Node(action, parent=v)
                v.children_expanded[action] = node
                return node

    def simulate(self, v):
        
        test = False
        '''
        if v.action == ((7, 9), 1):
            test = True
        '''
        for depth in range(self.MAX_DEPTH):
            if v.is_terminal():
                return (1.0*(self.DECAY**depth) if v.board.win else 0.0)

            action_selected = None
            
            action_value_list = []
            for action in v.get_successors():
                where = action[0]
                board_copy = v.board.deepcopy()
                board_copy[where[0]][where[1]] = v.board.whose_turn # 之前这边写错了
                value = self.eval_function(board_copy)
                action_value_list.append((action, value))
            if v.board.whose_turn == 1:
                action_selected, _ = max(action_value_list, key=lambda tup:tup[1])
            else:
                action_selected, _ = min(action_value_list, key=lambda tup:tup[1])
                
                if test:
                    print('action_selected: %s, value: %s'%(str(action_selected), _))
                    '''
                    for _action, _value in action_value_list:
                        if _action == ((14, 14), 2):
                            print('action_another: %s, value: %s'%(str(((14, 14), 2)), _value))
                    '''
                
            if action_selected is None:
                action_selected = random.choice( v.get_successors() )
            v = Node(action_selected, v)
        
        if test:
            v.board.print()
            print(self.eval_function(v.board))
        

        return self.eval_function(v.board)*(self.DECAY**depth)

    def back_propagate(self, v, reward):
        while v is not None:
            v.N += 1
            v.Q += reward if v.who() == 1 else 1-reward
            v = v.parent

    def uct_search(self):
        '''search主函数'''
        start_time = time.time()
        while time.time() - start_time < 5:
            v = self.select()
            #v = self.expand(v) #智障
            reward = self.simulate(v)
            self.back_propagate(v, reward)
        best_successor = self.root.best_successor_to_take()
        logDebug('After %s rounds of iteration'% self.root.N)
        logDebug('Found the best successor with win rate %s'% best_successor.win_rate())
        return best_successor.action

    def forward(self, action):
        who = action[1]
        if who == 2:
            if action not in self.root.children_expanded: # 如果对方下了我没有扩展过的节点，就新建那个节点
                self.root = Node(action, self.root)
                logDebug('Opponent\'s move %s was not expanded in previous searches'% str(action[0]))
            else:
                self.root = self.root.children_expanded[action]

        elif who == 1 and action not in self.root.children_expanded: # 对手先手，我下第二步会有这种情况
            logDebug('My move %s not in root.children_expanded %s'% (str(action), self.root.children_expanded) )
            self.root = Node(action, self.root)
        else:
            self.root = self.root.children_expanded[action]

        logDebug('Root node is now %s'% str(self.root.action))

def test():

    board.load('history4.txt', whose_turn=2)

    #board[7][9] = 1
    #board[11][12] = 2

    board.print()
    uct = UCT(board, critic_network.forward)

    action = uct.uct_search()
    print(uct.root.N)
    print(uct.root.children_expanded[action].Q)
    print(uct.root.children_expanded[action].N)
    
    print(uct.root.children_expanded[((9, 10), 1)].Q)
    print(uct.root.children_expanded[((9, 10), 1)].N)
    
    uct.forward(action)
    uct.root.board.print()
    '''
    board[13][11] = 2
    uct.forward( ((13, 11), 2) )
    uct.root.board.print()

    action = uct.uct_search()
    print(uct.root.N)
    uct.forward(action)
    uct.root.board.print()
    '''

if __name__ == '__main__':
    try:
        MAX_BOARD = 20
        board = Board(MAX_BOARD)

        CRITIC_NETWORK_SAVEPATH = RESOURCE_DIR + '/critic_network_new'
        critic_network = CriticNetwork(params=[len(board.features)*5 + 2, 60, 1], pattern_finder=board.pattern_finder)
        if os.path.exists(CRITIC_NETWORK_SAVEPATH):
            critic_network.layers = pickle.load(open(CRITIC_NETWORK_SAVEPATH, 'rb'))
            logDebug('Using existing model at '+CRITIC_NETWORK_SAVEPATH)
        else:
            logDebug(CRITIC_NETWORK_SAVEPATH)
            raise Exception()
        
        uct = UCT(board, critic_network.forward)

        #test()

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
            uct.reset()
            pp.pipeOut("OK")

        def isFree(x, y):
            return x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] == 0

        def brain_my(x, y):
            if isFree(x,y):
                board[x][y] = 1
                uct.forward( action=((x, y), 1) )
            else:
                pp.pipeOut("ERROR my move [{},{}]".format(x, y))

        def brain_opponents(x, y):
            if isFree(x,y):
                board[x][y] = 2
                uct.forward( action=((x, y), 2) )
            else:
                pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))

        def brain_block(x, y):
            if isFree(x,y):
                board[x][y] = 3
            else:
                pp.pipeOut("ERROR winning move [{},{}]".format(x, y))

        def brain_takeback(x, y):
            if x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] != 0:
                board[x][y] = 0
                return 0
            return 2

        def brain_turn():
            try:
                if pp.terminateAI:
                    return
                if board.whose_turn == None:
                    action = ((10, 10), 1)
                else:
                    action = uct.uct_search()
                where = action[0]
                pp.do_mymove(where[0], where[1])
                #uct.forward(action)
            except:
                logTraceBack()
                raise Exception("fuck")

        def brain_end():
            pass

        def brain_about():
            pp.pipeOut(pp.infotext)

        if DEBUG_EVAL:
            import win32gui
            def brain_eval(x, y):
                # TODO check if it works as expected
                wnd = win32gui.GetForegroundWindow()
                dc = win32gui.GetDC(wnd)
                rc = win32gui.GetClientRect(wnd)
                c = str(board[x][y])
                win32gui.ExtTextOut(dc, rc[2]-15, 3, 0, None, c, ())
                win32gui.ReleaseDC(wnd, dc)


        # "overwrites" functions in pisqpipe module
        pp.brain_init = brain_init
        pp.brain_restart = brain_restart
        pp.brain_my = brain_my
        pp.brain_opponents = brain_opponents
        pp.brain_block = brain_block
        pp.brain_takeback = brain_takeback
        pp.brain_turn = brain_turn
        pp.brain_end = brain_end
        pp.brain_about = brain_about
        if DEBUG_EVAL:
            pp.brain_eval = brain_eval


        pp.main()
    except:
        logTraceBack()
        raise Exception()