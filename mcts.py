import random
import time
import copy
import sys
import pisqpipe as pp
import math
from pisqpipe import DEBUG_EVAL, DEBUG
from Debug import logDebug, logTraceBack

sys.setrecursionlimit(100)

pp.infotext = 'name="pbrain-pyguaguagua", author="Iroh Cao", version="1.0", country="Shenzhen, China", www="https://github.com/stranskyjan/pbrain-pyrandom"'

MAX_BOARD = 20
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]
adjacent = []  # 邻近1格的空点
all_node = []  # 棋局顺序记录
opponents_node = []  # 对方下的棋记录
shou = 0   # 记录手数（总落子数）

###############################################
# Basic function
def check_board(board):
    for i in range(MAX_BOARD):
        for j in range(MAX_BOARD):
            if isFree(i,j) != 1:
                return False
    return True

def isCrossing(x, y):
    return x < 0 or y < 0 or x >= pp.width or y >= pp.height

def oppsite_who(who):
    if who == 1:
        return 2
    if who == 2:
        return 1

def check_win(board, x, y, who):
    # row
    left = 0
    right = 0
    while x-left-1 >= 0 and board[x-left-1][y] == who:
        left += 1
    while x+right+1 < MAX_BOARD and board[x+right+1][y] == who:
        right += 1
    if right + left + 1 >= 5:
        return True
    
    # col
    down = 0
    up = 0
    while y-down-1 >= 0 and board[x][y-down-1] == who:
        down += 1
    while y+up+1 < MAX_BOARD and board[x][y+up+1] == who:
        up += 1
    if up + down + 1 >= 5:
        return True

    # diag1
    upperLeft = 0
    lowerRight = 0
    while x-upperLeft-1 >= 0 and y+upperLeft+1 < MAX_BOARD and board[x-upperLeft-1][y+upperLeft+1] == who:
        upperLeft += 1
    while x+lowerRight+1 < MAX_BOARD and y-lowerRight-1 >= 0 and board[x+lowerRight+1][y-lowerRight-1] == who:
        lowerRight += 1
    if lowerRight + upperLeft + 1 >= 5:
        return True

    # diag2
    lowerLeft = 0
    upperRight = 0
    while x-lowerLeft-1 >= 0 and y-lowerLeft-1 >= 0 and board[x-lowerLeft-1][y-lowerLeft-1] == who:
        lowerLeft += 1
    while x+upperRight+1 < MAX_BOARD and y+upperRight+1 < MAX_BOARD and board[x+upperRight+1][y+upperRight+1] == who:
        upperRight += 1
    if upperRight + lowerLeft + 1 >= 5:
        return True
    
    return False

def check_opponents(board, opponents_node):
    for i in range(MAX_BOARD):
        for j in range(MAX_BOARD):
            if board[i][j] == 2 and (i,j) not in opponents_node:
                return i, j             

###############################################
# Heuristic function
def my_heuristic(board, x, y, who):
    my_heuristic = 0.0
    delta = 0.89
    # row
    left = 0
    right = 0
    row_opponent = 0
    while x-left-1 >= 0:
        if board[x-left-1][y] == who:
            left += 1
        elif board[x-left-1][y] == oppsite_who(who):
            row_opponent += 1
            break
        elif board[x-left-1][y] == 0:
            break
        if x-left-2 < 0:
            row_opponent += 1
            break        
    while x+right+1 < MAX_BOARD:
        if board[x+right+1][y] == who:
            right += 1
        elif board[x+right+1][y] == oppsite_who(who):
            row_opponent += 1
            break
        elif board[x+right+1][y] == 0:
            break
        if x+right+2 >= MAX_BOARD:
            row_opponent += 1
            break  
    if right + left >= 4:
        my_heuristic += 10 ** 5
    else:
        if row_opponent == 0:
            my_heuristic += 10 ** (left + right + 1.0) 
        elif row_opponent == 1 and right + left > 0:
            my_heuristic += 10 ** (left + right) 
        elif row_opponent == 2:
            my_heuristic += 0
    
    # col
    down = 0
    up = 0
    col_opponent = 0
    while y-down-1 >= 0:
        if board[x][y-down-1] == who:
            down += 1
        elif board[x][y-down-1] == oppsite_who(who):
            col_opponent += 1
            break
        elif board[x][y-down-1] == 0:
            break
        if y-down-2 < 0:
            col_opponent += 1
            break        
    while y+up+1 < MAX_BOARD:
        if board[x][y+up+1] == who:
            up += 1
        elif board[x][y+up+1] == oppsite_who(who):
            col_opponent += 1
            break
        elif board[x][y+up+1] == 0:
            break
        if y+up+2 >= MAX_BOARD:
            col_opponent += 1
            break 
    if up + down >= 4:
        my_heuristic += 10 ** 5
    else:
        if col_opponent == 0:
            my_heuristic += 10 ** (up + down + 1.0)
        elif col_opponent == 1 and up + down > 0:
            my_heuristic += 10 ** (up + down)
        elif col_opponent == 2:
            my_heuristic += 0

    # diag1  
    upperLeft = 0
    lowerRight = 0
    diag1_opponent = 0
    while x-upperLeft-1 >= 0 and y+upperLeft+1 < MAX_BOARD:
        if board[x-upperLeft-1][y+upperLeft+1] == who:
            upperLeft += 1
        elif board[x-upperLeft-1][y+upperLeft+1] == oppsite_who(who):
            diag1_opponent += 1
            break
        elif board[x-upperLeft-1][y+upperLeft+1] == 0:
            break
        if x-upperLeft-2 < 0 or y+upperLeft+2 >= MAX_BOARD:
            diag1_opponent += 1
            break        
    while x+lowerRight+1 < MAX_BOARD and y-lowerRight-1 >= 0:
        if board[x+lowerRight+1][y-lowerRight-1] == who:
            lowerRight += 1
        elif board[x+lowerRight+1][y-lowerRight-1] == oppsite_who(who):
            diag1_opponent += 1
            break
        elif board[x+lowerRight+1][y-lowerRight-1] == 0:
            break
        if x+lowerRight+2 >= MAX_BOARD or y-lowerRight-2 < 0:
            diag1_opponent += 1
            break 
    if lowerRight + upperLeft >= 4:
        my_heuristic += 10 ** 5
    else:
        if diag1_opponent == 0:
            my_heuristic += 10 ** (lowerRight + upperLeft + 1.0)
        elif diag1_opponent == 1 and lowerRight + upperLeft > 0:
            my_heuristic += 10 ** (lowerRight + upperLeft)
        elif diag1_opponent == 2:
            my_heuristic += 0

    # diag2 
    lowerLeft = 0
    upperRight = 0
    diag2_opponent = 0
    while x-lowerLeft-1 >= 0 and y-lowerLeft-1 >= 0:
        if board[x-lowerLeft-1][y-lowerLeft-1] == who:
            lowerLeft += 1
        elif board[x-lowerLeft-1][y-lowerLeft-1] == oppsite_who(who):
            diag2_opponent += 1
            break
        elif board[x-lowerLeft-1][y-lowerLeft-1] == 0:
            break
        if x-lowerLeft-2 < 0 and y-lowerLeft-2 < 0:
            diag2_opponent += 1
            break        
    while x+upperRight+1 < MAX_BOARD and y+upperRight+1 < MAX_BOARD:
        if board[x+upperRight+1][y+upperRight+1] == who:
            upperRight += 1
        elif board[x+upperRight+1][y+upperRight+1] == oppsite_who(who):
            diag2_opponent += 1
            break
        elif board[x+upperRight+1][y+upperRight+1] == 0:
            break
        if x+upperRight+2 >= MAX_BOARD and y+upperRight+2 >= MAX_BOARD:
            diag2_opponent += 1
            break 
    if upperRight + lowerLeft >= 4:
        my_heuristic += 10 ** 5
    else:
        if diag2_opponent == 0:
            my_heuristic += 10 ** (upperRight + lowerLeft + 1.0) 
        elif diag2_opponent == 1 and upperRight + lowerLeft > 0:
            my_heuristic += 10 ** (upperRight + lowerLeft)
        elif diag2_opponent == 2:
            my_heuristic += 0

    # 继续考虑跳3的情况 - OO O - or - O OO - 考虑跳2的情况 - O O -
    for i in range(-1, 2, 1):
        for j in range(-1, 2, 1):
            if i == 0 and j == 0:
                continue
            if isCrossing(x+4*i, y+4*j) != 1 and isCrossing(x-3*i, y-3*j) != 1:
                 # 考虑跳4的情况 - OO O - or - O OO -
                if board[x-1*i][y-1*j] == who and board[x-2*i][y-2*j] == 0 and board[x+1*i][y+1*j] == 0 and  board[x+2*i][y+2*j] == who and board[x+3*i][y+3*j] == 0:
                    my_heuristic += 900 
                elif board[x+1*i][y+1*j] == 0 and board[x+2*i][y+2*j] == who and board[x+3*i][y+3*j] == who and board[x-1*i][y-1*j] == 0 and board[x+4*i][y+4*j] == 0:
                    my_heuristic += 900
                elif board[x+1*i][y+1*j] == who and board[x+2*i][y+2*j] == 0 and board[x+3*i][y+3*j] == who and board[x-1*i][y-1*j] == 0 and board[x+4*i][y+4*j] == 0:
                    my_heuristic += 900
                # 继续考虑眠跳4的情况 -XOO O - or -XO OO -
                elif board[x+1*i][y+1*j] == 0 and board[x-1*i][y-1*j] == who and board[x-2*i][y-2*j] == oppsite_who(who) and board[x+2*i][y+2*j] == who and board[x+3*i][y+3*j] == 0:
                    my_heuristic += 80
                elif board[x+1*i][y+1*j] == who and board[x+2*i][y+2*j] == 0 and board[x+3*i][y+3*j] == who and board[x-1*i][y-1*j] == oppsite_who(who) and board[x+4*i][y+4*j] == 0:
                    my_heuristic += 80
                elif board[x+1*i][y+1*j] == 0 and board[x+2*i][y+2*j] == who and board[x+3*i][y+3*j] == who and board[x-1*i][y-1*j] == 0 and board[x+4*i][y+4*j] == oppsite_who(who):
                    my_heuristic += 80
                elif board[x+1*i][y+1*j] == 0 and board[x+2*i][y+2*j] == who and board[x+3*i][y+3*j] == who and board[x-1*i][y-1*j] == oppsite_who(who) and board[x+4*i][y+4*j] == 0:
                    my_heuristic += 80
                elif board[x+1*i][y+1*j] == who and board[x-1*i][y-1*j] == 0 and board[x-2*i][y-2*j] == who and board[x+2*i][y+2*j] == 0 and board[x-3*i][y-3*j] == oppsite_who(who):
                    my_heuristic += 80
                elif board[x+1*i][y+1*j] == who and board[x+2*i][y+2*j] == 0 and board[x+3*i][y+3*j] == who and board[x-1*i][y-1*j] == 0 and board[x+4*i][y+4*j] == oppsite_who(who):
                    my_heuristic += 80
            # -XOOO O-
            if isCrossing(x-5*i, y-5*j) != 1:
                if board[x-1*i][y-1*j] == 0  and board[x-2*i][y-2*j] == who and board[x-3*i][y-3*j] == who and board[x-4*i][y-4*j] == who and board[x-5*i][y-5*j] == oppsite_who(who):
                    my_heuristic += 800
            # -XOO OO-   
                elif board[x-1*i][y-1*j] == who  and board[x-2*i][y-2*j] == 0 and board[x-3*i][y-3*j] == who and board[x-4*i][y-4*j] == who and board[x-5*i][y-5*j] == oppsite_who(who):
                    my_heuristic += 800
    
    if isCrossing(x + 1,y + 2) != 1 and board[x+1][y+2] == who:
        my_heuristic += 10
    if isCrossing(x - 1,y + 2) != 1 and board[x-1][y+2] == who:
        my_heuristic += 10
    if isCrossing(x + 1,y - 2) != 1 and board[x+1][y-2] == who:
        my_heuristic += 10
    if isCrossing(x - 1,y - 2) != 1 and board[x-1][y-2] == who:
        my_heuristic += 10
    if isCrossing(x + 2,y + 1) != 1 and board[x+2][y+1] == who:
        my_heuristic += 10
    if isCrossing(x + 2,y - 1) != 1 and board[x+2][y-1] == who:
        my_heuristic += 10
    if isCrossing(x - 2,y + 1) != 1 and board[x-2][y+1] == who:
        my_heuristic += 10
    if isCrossing(x - 2,y - 1) != 1 and board[x-2][y-1] == who:
        my_heuristic += 10

    return my_heuristic * delta

def opponents_heuristic(board, x, y, who):
    opponents_heuristic = 0.0
    for i in range(-1, 2, 1):
        for j in range(-1, 2, 1):
            if i == 0 and j == 0:
                continue
            opponents = 0.0
            my = 0.0
            for k in range(1, 6):
                if isFree(x + i * k, y + j * k):
                    break
                else:
                    if isCrossing(x + i * k, y + j * k):
                        # opponents = pow(opponents, 0.5)
                        break
                    if board[x + i * k][y + j * k] == who:
                        my = 1.0
                        break
                    else:
                        opponents = opponents + 1.0
            if my == 1.0 and opponents > 1:
                opponents_heuristic = opponents_heuristic - 10 ** (opponents-1.0) 
            elif my == 0 and opponents > 0:
                opponents_heuristic = opponents_heuristic - 10 ** opponents
    # 继续考虑跳3的情况 -OO O-
    for i in range(-1, 2, 1):
        for j in range(-1, 2, 1):
            if i == 0 and j == 0:
                continue
            if isCrossing(x+5*i, y+5*j) != 1:
                 # 考虑跳3的情况 -XOO O - or - OXOO - or - OO OX-        此处可能有误，要修改
                if  board[x+1*i][y+1*j] == oppsite_who(who) and board[x+2*i][y+2*j] == oppsite_who(who) and board[x+3*i][y+3*j] == 0 and board[x+4*i][y+4*j] == oppsite_who(who) and board[x+5*i][y+5*j] == 0:
                    opponents_heuristic -= 900 
                elif board[x+1*i][y+1*j] == oppsite_who(who) and board[x+2*i][y+2*j] == 0 and board[x+3*i][y+3*j] == oppsite_who(who) and board[x+4*i][y+4*j] == oppsite_who(who) and board[x+5*i][y+5*j] == 0:
                    opponents_heuristic -= 900
            if isCrossing(x-2*i, y-2*j) != 1 and isCrossing(x+3*i, y+3*j) != 1:
                if board[x-2*i][y-2*j] == 0 and board[x-1*i][y-1*j] == oppsite_who(who) and board[x+1*i][y+1*j] == oppsite_who(who) and board[x+2*i][y+2*j] == oppsite_who(who) and board[x+3*i][y+3*j] == 0:
                    opponents_heuristic -= 900
            if isCrossing(x-1*i, y-1*j) != 1 and isCrossing(x+3*i, y+3*j) != 1:
            # -OOOXO-
                if board[x-1*i][y-1*j] == oppsite_who(who) and board[x+1*i][y+1*j] == oppsite_who(who) and board[x+2*i][y+2*j] == oppsite_who(who) and board[x+3*i][y+3*j] == oppsite_who(who):
                    opponents_heuristic -= 9000
            # -OXOOO-
            if isCrossing(x-3*i, y-3*j) != 1 and isCrossing(x+1*i, y+1*j) != 1:    
                if board[x-3*i][y-3*j] == oppsite_who(who) and board[x-2*i][y-2*j] == oppsite_who(who) and board[x-1*i][y-1*j] == oppsite_who(who) and board[x+1*i][y+1*j] == oppsite_who(who):
                    opponents_heuristic -= 9000
            # -OOXOO-
            if isCrossing(x-2*i, y-2*j) != 1 and isCrossing(x+2*i, y+2*j) != 1:    
                if board[x-2*i][y-2*j] == oppsite_who(who) and board[x-1*i][y-1*j] == oppsite_who(who) and board[x+1*i][y+1*j] == oppsite_who(who) and board[x+2*i][y+2*j] == oppsite_who(who):
                    opponents_heuristic -= 9000

    return opponents_heuristic

def confront_heuristic(board, x, y, who): 
    """The function calculate the confront_heuristic after adding an adjacent point"""
    """delete each old heuristic value in 8 directions"""
    return my_heuristic(board, x, y, who) - opponents_heuristic(board, x, y, who)

###############################################
# Adjacent function
def Adjacent(board):
    """It is a function for choosing the adjacent free point of full point in the board"""   
    adjacent = []
    for x in range(MAX_BOARD):
        for y in range(MAX_BOARD):
            if isFree(x, y):
                tag = 0
                for i in range(-2, 3, 1):
                    for j in range(-2, 3, 1):
                        if isCrossing(x+i,y+j):
                            continue
                        if isFree(x+i,y+j):
                            continue
                        else:
                            tag = 1
                if tag == 1:
                    adjacent.append((x,y))                        
    return adjacent

def Adjacent1(board):
    """It is a function for choosing the adjacent free point of full point in the board"""   
    adjacent = []
    for x in range(MAX_BOARD):
        for y in range(MAX_BOARD):
            if isFree(x, y):
                tag = 0
                for i in range(-1, 2, 1):
                    for j in range(-1, 2, 1):
                        if isCrossing(x+i,y+j):
                            continue
                        if isFree(x+i,y+j):
                            continue
                        else:
                            tag = 1
                if tag == 1:
                    adjacent.append((x,y))                        
    return adjacent

def Adjacent_1(board, old_adjacent, x, y):
    """It is a function for choosing the 1 point adjacent free points of full point in the board"""   
    adjacent = []
    adjacent = old_adjacent
    adjacent.remove((x,y))
    for i in range(-1, 2, 1):
        for j in range(-1, 2, 1):
            if isFree(x+i,y+j):
                if isCrossing(x+i,y+j):
                    continue
                if (x+i,y+j) in adjacent:
                    continue
                else:
                    adjacent.append((x+i,y+j))
            else:
                continue                           
    return adjacent

def Adjacent_2(board, old_adjacent, x, y):
    """It is a function for choosing the 2 point adjacent free points of full point in the board"""   
    adjacent = []
    adjacent = old_adjacent
    adjacent.remove((x,y))
    for i in range(-2, 3, 1):
        for j in range(-2, 3, 1):
            if isFree(x+i,y+j):
                if isCrossing(x+i,y+j):
                    continue
                if (x+i,y+j) in adjacent:
                    continue
                else:
                    adjacent.append((x+i,y+j))
            else:
                continue                           
    return adjacent

def Pruning_Adjacent(board, adjacent, who):  #  现在取的是前3的点
    """It is a function for choosing the adjacent free point of full point in the board"""   
    Pruning_Adjacent = []
    score = {}
    for (x,y) in adjacent:
        score[(x,y)] = confront_heuristic(board, x, y, who)
    rank = sorted(score.items(), key = lambda item:item[1], reverse = True)
    for i in range(0, 3):
        Pruning_Adjacent.append(rank[i][0])
    return Pruning_Adjacent

def Pruning_AdjacentInRange(board, adjacent, who):  #  现在取的是前3且>=1000的点
    """It is a function for choosing the adjacent free point of full point in the board"""   
    Pruning_Adjacent = []
    score = {}
    for (x,y) in adjacent:
        score[(x,y)] = confront_heuristic(board, x, y, who)
    rank = sorted(score.items(), key = lambda item:item[1], reverse = True)
    for i in range(0, 3):
        if rank[i][0] >= 1000:
            Pruning_Adjacent.append(rank[i][0])
    if len(Pruning_Adjacent) == 0:
        Pruning_Adjacent.append(rank[0][0])
    return Pruning_Adjacent

###############################################
# UCT
class MCTS_UCT(object):
    """
    Use Monte Carlo Tree Search with pure-MCTS
    """ 
    def __init__(self, board, play_turn, time=10, max_actions=100):
 
        self.board = board
        self.play_turn = play_turn   # 出手顺序
        self.calculation_time = float(time-1)   # 最大运算时间
        self.max_actions = max_actions   # 每次模拟对局最多进行的步数
        self.board_availables = Adjacent(board)  # 使用Adjacent函数来选择availables
        self.confident = 1.96   # UCB中的常数，可以修改，但不建议
        self.plays = {}   # 记录着法参与模拟的次数，键形如(player, move)，即（玩家，落子）
        self.wins = {}    # 记录着法获胜的次数
        self.max_depth = 1

    def get_action(self): # return move 
        # 每次计算下一步时都要清空plays和wins表，因为经过AI和玩家的2步棋之后，整个棋盘的局面发生了变化，原来的记录已经不适用了——
        # 原先普通的一步现在可能是致胜的一步，如果不清空，会影响现在的结果，导致这一步可能没那么“致胜”了
        self.plays = {} 
        self.wins = {}
        simulations = 0
        for x, y in self.board_availables:
            if check_win(board, x, y, 1):
                return (x, y)
            if check_win(board, x, y, 2):
                return (x, y)
        
        begin = time.time()
        while time.time() - begin < self.calculation_time:
            board_copy = copy.deepcopy(self.board)    # 模拟会修改board的参数，所以必须进行深拷贝，与原board进行隔离
            play_turn_copy = copy.deepcopy(self.play_turn)    # 每次模拟都必须按照固定的顺序进行，所以进行深拷贝防止顺序被修改
            self.run_simulation(board_copy, play_turn_copy)    # 进行MCTS-UCT
            simulations += 1         #可以尝试尽可能增加simulation的总数，总数越大说明MCTS-UCT采样越多，可能的改进有、修改adjacent函数、降低heuristic函数复杂度、剪枝等，均可以尝试。
        # logDebug(simulations)                     #  这里计算每次simulation的总次数，加入simulation的次数小于100就说明时间复杂度太高（假如每次选前三的点，五轮迭代就是3*3*3*3*3>100）
        move = self.select_one_move() # 选择最佳着法
        #location = self.board.move_to_location(move) 
        return move

    def select_one_move(self):
        data= {}
        availables = Pruning_Adjacent(board, self.board_availables, 1)
        for move in availables:  # 选择胜率最高的着法
            data[move] = (self.wins.get((1, move), 0) /
            self.plays.get((1, move), 1)) + confront_heuristic(board, move[0], move[1], 1)/(100000.0)   # 在select_one_move过程中，可以加入ADP的值，进行归一，我现在用的依旧是我的heuristic，你可以删了
        # logDebug(sorted(data.items(), key = lambda item:item[1], reverse = True))
        move, percent_wins = sorted(data.items(), key = lambda item:item[1], reverse = True)[0]
        return move

    def get_player(self, players):   # 获取出手的玩家
        p = players.pop(0)
        players.append(p)
        return p
    
    def run_simulation(self, board, play_turn):
        """
        MCTS main process
        """ 
        plays = self.plays
        wins = self.wins
        adjacent = self.board_availables   # 使用Adjacent函数来选择availables
        player = self.get_player(play_turn) # 获取当前出手的玩家
        visited_states = set() # 记录当前路径上的全部着法
        winner = -1
        expand = True
 
        # Simulation
        for t in range(1, self.max_actions + 1):
            # Selection
            # 如果所有着法都有统计信息，则获取UCB最大的着法
            availables = Pruning_Adjacent(board, adjacent, player)

            tag = 0
            for (x,y) in availables:
                if check_win(board, x, y, player):
                    move = (x,y)
                    tag = 1
                    break
                if check_win(board, x, y, oppsite_who(player)):
                    move = (x,y)
                    tag = 1
                    break
            if tag == 0:  
                if player == 1:             
                    if all(plays.get((player, move)) for move in availables):
                        log_total = math.log(sum(plays[(player, move)] for move in availables))            
                        value, move = max(
                            (((wins[(player, move)] / plays[(player, move)]) +
                            math.sqrt(self.confident * log_total / plays[(player, move)])) + confront_heuristic(board, move[0], move[1], player)/100000.0, move) 
                            for move in availables)
                    else:
                        # 否则随机选择一个着法
                        move = random.sample(availables, int(len(availables)))[0]
                elif player == 2:
                    value, move = max(
                        (my_heuristic(board, move[0], move[1], player), move) 
                        for move in availables)

            
            board[move[0]][move[1]] = player   # update the board
            adjacent = Adjacent_1(board, adjacent, move[0], move[1])
            
            # Expand
            # 每次模拟最多扩展一次，每次扩展只增加一个着法
            if expand and (player, move) not in plays:
                expand = False
                plays[(player, move)] = 0
                wins[(player, move)] = 0
                if t > self.max_depth:
                    self.max_depth = t
 
            visited_states.add((player, move))
            # is_full = not len(availables)
            if check_win(board, move[0], move[1], player):
                winner = player
                break
            player = self.get_player(play_turn)
        
        last_x = move[0]
        last_y = move[1]   # 记录simulation最后一步的坐标
        # Back-propagation
        for player, move in visited_states:
            if (player, move) not in plays:
                continue
            plays[(player, move)] += 1 # 当前路径上所有着法的模拟次数加1
            if player == winner:
                wins[(player, move)] += 1 # 获胜玩家的所有着法的胜利次数加1
            elif winner == -1:
                wins[(player, move)] += 0.5    # 在Back-propagation 部分，可以把simulation直到达到maxaction都没成功时的胜率加到这里，我现在预设的是0.5
            elif winner != player and winner != -1:
                wins[(player, move)] += 0.0
 
    def __str__(self):
        return "GUAGUAGUAGUA-AI"

###############################################
# Orginal Function 
def brain_init():
    if pp.width < 5 or pp.height < 5:
        pp.pipeOut("ERROR size of the board")
        return
    if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
        pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
        return
    pp.pipeOut("OK")

def brain_restart():
    global adjacent
    global opponents_node
    global shou
    shou = 0
    adjacent = []
    opponents_node = []
    for x in range(pp.width):
        for y in range(pp.height):
            board[x][y] = 0
    pp.pipeOut("OK")

def isFree(x, y):
	return x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] == 0

def brain_my(x, y):
	if isFree(x,y):
		board[x][y] = 1
	else:
		pp.pipeOut("ERROR my move [{},{}]".format(x, y))

def brain_opponents(x, y):
	if isFree(x,y):
		board[x][y] = 2
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
        i = 0
        while True:
            global board
            global adjacent
            global opponents_node
            global shou
            if check_board(board):
                x = int(pp.width/2)
                y = int(pp.height/2)
            else:
                shou += 1
                if shou == 1:
                    # opponents_x, opponents_y = check_opponents(board, opponents_node)
                    x,y = Adjacent1(board)[0]
                else:
                    play_turn = [1,2,1,2,1,2,1,2,1,2,1,2]
                    if shou < 10:
                        UCT = MCTS_UCT(board, play_turn, time=5, max_actions=9)
                    else:
                        UCT = MCTS_UCT(board, play_turn, time=6, max_actions=9)
                    move = UCT.get_action()
                    x,y = move
            # logDebug((x,y))
            # heuristic = confront_heuristic(board, x, y, 1)
            # logDebug(my_heuristic(board, x, y, 1))
            # logDebug(opponents_heuristic(board, x, y, 1))
            # logDebug(heuristic)
            shou += 1
            i += 1
            if pp.terminateAI:
                return
            if isFree(x,y):
                break
        if i > 1:
            pp.pipeOut("DEBUG {} coordinates didn't hit an empty field".format(i))
        pp.do_mymove(x, y)
    except:
        # logTraceBack()
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

def main():
	pp.main()

if __name__ == "__main__":
	main()

###############################################