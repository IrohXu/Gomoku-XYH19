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
from board_info_helper import *

START_TIME = time.time()
TIME_LIMIT = 90
MAX_BOARD = 20
board = Board(MAX_BOARD)

CRITIC_NETWORK_SAVEPATH = RESOURCE_DIR + '/critic_network_nnew'
critic_network = CriticNetwork(params=[len(board.features)*5 + 2, 60, 1], pattern_finder=board.pattern_finder)

if os.path.exists(CRITIC_NETWORK_SAVEPATH):
    critic_network.layers = pickle.load(open(CRITIC_NETWORK_SAVEPATH, 'rb'))
    logDebug('Using existing model at '+CRITIC_NETWORK_SAVEPATH)
else:
    logDebug(CRITIC_NETWORK_SAVEPATH)
    raise Exception()


EVAL_FUNCTION = critic_network.forward

class Node():
    def __init__(self, action, parent, board=None):
        where, who = action

        self.action = action
        self.children_expanded = {}
        self.adjacents = None
        self.successors = None
        self.parent = parent
        self.N = 0.0
        self.Q = 0.0
        self.eval_function = EVAL_FUNCTION
        
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
        return self.Q/self.N + 0.4*math.sqrt(2*math.log(self.parent.N)/self.N) # 对自己的simulation有信心的话就把探索系数设小一点
    
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
    def get_adjacents(self):
        if self.adjacents is None:
            if self.parent is not None:
                parent_adjacents = self.parent.get_adjacents()
                where = self.action[0]
                new_adjacents = Adjacent4Point(self.board, where)
                self.adjacents = parent_adjacents.union(new_adjacents)
                self.adjacents.discard(where)
            
            else:
                self.adjacents = set(Adjacent(self.board))
        
        return self.adjacents 

    def get_successors(self):
        if self.successors is None:
            if self.board.win is None:
                assert self.board.whose_turn != self.who()
                adjacents = self.get_adjacents()
                #pruned_adjacents = list(adjacents)
                pruned_adjacents = self.heuristic_pruning(list(adjacents))
                pruned_adjacents = self.eval_function_pruning(pruned_adjacents)
                self.successors = list(map(lambda where:(where, self.board.whose_turn), pruned_adjacents))
            else:
                self.successors = []
        return self.successors
    
    def is_terminal(self):
        return len(self.get_successors()) == 0

    def is_determined(self):
        return len(self.get_successors()) == 1
    
    def is_expandable(self):
        return len(self.children_expanded) < len(self.get_successors())

######################################################################################    

    
    


    def heuristic_pruning(self, adjacent):
        '''
        返回一个元祖([], int):  (avaliable, win)
        '''
        pruning = []
        inital_two_total = count_live_two_op(self.board, self.board.whose_turn) + count_live_three_op(self.board, self.board.whose_turn) 
        #逐个adjacent遍历，进行剪枝
        for (x,y) in adjacent:
            who = self.board.whose_turn
            # 如果下完这一步直接五连
            if check_win(board, x, y, who):
                pruning = [(x, y)]
                return pruning

        #逐个adjacent遍历，进行剪枝
        for (x,y) in adjacent:
            temp_board = self.board.deepcopy()
            who = temp_board.whose_turn
            temp_board[x][y] = who
            # 当敌方有冲四机会的时候，必须防御，没去防御的都跳过
            if count_rest_four_op(temp_board, who) >= 1:
                continue
            # 当敌方没有冲四机会的时候
            else:
                if count_live_four_my(temp_board, who) >= 1:
                    pruning = [(x, y)]
                    return pruning
                # 当有两个冲四机会的时候，必胜
                if count_rest_four_my(temp_board, who) >= 2:
                    pruning = [(x, y)]
                    return pruning
                # 有一个冲四和一个冲三
                if count_rest_four_my(temp_board, who) >= 1 and count_live_three_my(temp_board, who) >= 1:
                    pruning = [(x, y)]
                    return pruning
                # 当下一步对手没法冲四，而我方的冲四+活三>=2必胜
                if count_rest_three_op(temp_board, who) + count_live_three_op(temp_board, who) == 0 and count_live_three_my(temp_board, who) + count_rest_four_my(temp_board, who) >= 2:
                    pruning = [(x, y)]
                    return pruning
                if count_rest_four_my(temp_board, who) >= 1:
                    pruning.append((x,y))
                elif count_live_three_op(temp_board, who) >= 1:
                    continue
                elif count_live_two_op(temp_board, who) + count_live_three_op(temp_board, who) - inital_two_total >= 2:
                    pruning.append((x,y))
                else:
                    pruning.append((x,y))
        return pruning

    def eval_function_pruning(self, adjacent):
        LIMIT = 20
        if len(adjacent) <= LIMIT:
            return adjacent

        where_value_list = []
        for where in adjacent:
            board_copy = self.board.deepcopy()
            board_copy[where[0]][where[1]] = self.board.whose_turn # 之前这边写错了
            value = self.eval_function(board_copy)
            where_value_list.append((where, value))
        if self.board.whose_turn == 1:
            pruned = map(lambda tup:tup[0], sorted(where_value_list, key=lambda tup:tup[1], reverse=True)[0:LIMIT])
        else:
            pruned = map(lambda tup:tup[0], sorted(where_value_list, key=lambda tup:tup[1])[0:LIMIT])
        pruned = list(pruned)

        
        return pruned
            

##########################################################################################

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
        if v.action == ((12, 7), 1):
            test = True
            v.board.print()
            print(v.get_successors())
        '''
        for depth in range(self.MAX_DEPTH):
            if v.is_terminal():
                break

            action_selected = None
            
            #action_selected = self.eval_function_decision(v.board, v.get_successors())
            
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
                    print('adjacents: %s'%str(v.get_adjacents()))
                    print('successors: %s'%str(v.heuristic_pruning(v.get_adjacents())))


            if action_selected is None:
                action_selected = random.choice( v.get_successors() )

            v = Node(action_selected, v)
        

        if v.is_terminal():
            Q = 1.0 if v.board.win else 0.0

        else:
            Q = self.eval_function(v.board)

        Q = 0.5 + (Q-0.5)*self.DECAY**depth
        
        if test:
            print('final Q: %s'%Q)
            v.board.print()
            print('whose turn: %s'%v.board.whose_turn)

        return Q

    def back_propagate(self, v, reward):
        while v is not None:
            v.N += 1
            v.Q += reward if v.who() == 1 else 1-reward
            v = v.parent

    def eval_function_decision(self, board, successors):
        action_value_list = []
        for action in successors:
            where = action[0]
            board_copy = board.deepcopy()
            board_copy[where[0]][where[1]] = board.whose_turn # 之前这边写错了
            value = self.eval_function(board_copy)
            action_value_list.append((action, value))

        if board.whose_turn == 1:
            action_selected, _ = max(action_value_list, key=lambda tup:tup[1])
            logDebug('Chose action %s with max value %s'%(str(action_selected), _))
        else:
            action_selected, _ = min(action_value_list, key=lambda tup:tup[1])
            logDebug('Chose action %s with min value %s'%(str(action_selected), _))
        logDebug('Action Value List: '+str(action_value_list))
        return action_selected

    def uct_search(self):
        '''search主函数'''
        if self.root.is_terminal():
            logDebug('Gave up')
            successors_from_adjacents = list(map(lambda where:(where, self.root.board.whose_turn), list(self.root.get_adjacents())))
            logDebug('Choosing an action from '+str(successors_from_adjacents))
            action_selected = self.eval_function_decision(self.root.board, successors_from_adjacents)
            return action_selected
        elif self.root.is_determined():
            logDebug('Took a step determined by the pruning function')
            return self.root.get_successors()[0]
        else:
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
    
    #board.load('history5.txt', whose_turn=2)

    #board[7][9] = 1
    #board[11][12] = 2

    board.print()
    uct = UCT(board, critic_network.forward)

    whose_turn = 1
    f = open('history5.txt', 'r')
    for line in f.readlines():
        start = line.index('[')
        end = line.index(']')+1
        x, y = eval(line[start:end])
        board[x][y] = whose_turn
        uct.forward( action=((x, y), whose_turn) )
        whose_turn = 1 if whose_turn==2 else 2
        uct.root.board.print()
        print('Adjacents: '+str(uct.root.get_adjacents()))
        uct.root.board.print(marks=uct.root.get_adjacents())
    board.print()

    action = uct.uct_search()
    print(uct.root.N)
    
    print(uct.root.children_expanded[action].Q)
    print(uct.root.children_expanded[action].N)
    
    print(action)
    
    print(uct.root.children_expanded[((11, 6), 1)].Q)
    print(uct.root.children_expanded[((11, 6), 1)].N)

    #for action in uct.root.children_expanded:
    #    print(str(action)+': '+str(uct.root.children_expanded[action].win_rate()))
    '''
    print(uct.root.children_expanded[((10, 11), 1)].Q)
    print(uct.root.children_expanded[((10, 11), 1)].N)
    '''
    
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
        global START_TIME
        START_TIME = time.time()
        pp.pipeOut("OK")

    def isFree(x, y):
        return x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] == 0

    def brain_my(x, y):
        if isFree(x,y):
            board[x][y] = 1
            uct.forward( action=((x, y), 1) )
            logDebug(uct.root.board)
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
                if time.time()-START_TIME > TIME_LIMIT - 6:
                    logDebug('Running out of time, use ADP instead')
                    successors_from_adjacents = list(map(lambda where:(where, uct.root.board.whose_turn), list(uct.root.get_adjacents())))
                    logDebug('Choosing an action from '+str(successors_from_adjacents))
                    action = uct.eval_function_decision(uct.root.board, successors_from_adjacents)
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