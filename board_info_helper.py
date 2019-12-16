import random
import itertools
MAX_BOARD = 20

def generate_board_value_lists(board, x, y, who):

    # row
    old_row_list = [board[x][y]]
    new_row_list = [who]
    left = 0
    right = 0
    while x-left-1 >= 0:
        old_row_list.insert(0, board[x-left-1][y])
        new_row_list.insert(0, board[x-left-1][y])
        left += 1 
    while x+right+1 < MAX_BOARD:
        old_row_list.append(board[x+right+1][y])
        new_row_list.append(board[x+right+1][y])
        right += 1
    
    # col
    old_col_list = [board[x][y]]
    new_col_list = [who]
    down = 0
    up = 0
    while y-down-1 >= 0:
        old_col_list.insert(0, board[x][y-down-1])
        new_col_list.insert(0, board[x][y-down-1])
        down += 1
    while y+up+1 < MAX_BOARD:
        old_col_list.append(board[x][y+up+1])
        new_col_list.append(board[x][y+up+1])
        up += 1


    # diag1
    old_diag1_list = [board[x][y]]
    new_diag1_list = [who]
    upperLeft = 0
    lowerRight = 0
    while x-upperLeft-1 >= 0 and y+upperLeft+1 < MAX_BOARD:
        old_diag1_list.insert(0, board[x-upperLeft-1][y+upperLeft+1])
        new_diag1_list.insert(0, board[x-upperLeft-1][y+upperLeft+1])
        upperLeft += 1
    while x+lowerRight+1 < MAX_BOARD and y-lowerRight-1 >= 0:
        old_diag1_list.append(board[x+lowerRight+1][y-lowerRight-1])
        new_diag1_list.append(board[x+lowerRight+1][y-lowerRight-1])
        lowerRight += 1


    # diag2
    old_diag2_list = [board[x][y]]
    new_diag2_list = [who]
    lowerLeft = 0
    upperRight = 0
    while x-lowerLeft-1 >= 0 and y-lowerLeft-1 >= 0:
        old_diag2_list.insert(0, board[x-lowerLeft-1][y-lowerLeft-1])
        new_diag2_list.insert(0, board[x-lowerLeft-1][y-lowerLeft-1])
        lowerLeft += 1
    while x+upperRight+1 < MAX_BOARD and y+upperRight+1 < MAX_BOARD:
        old_diag2_list.append(board[x+upperRight+1][y+upperRight+1])
        new_diag2_list.append(board[x+upperRight+1][y+upperRight+1])
        upperRight += 1

    return [old_row_list, old_col_list, old_diag1_list, old_diag2_list], [new_row_list, new_col_list, new_diag1_list, new_diag2_list]

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

def isCrossing(x, y):
    return x < 0 or y < 0 or x >= MAX_BOARD or y >= MAX_BOARD

def Adjacent(board, shuffle=True):
    """It is a function for choosing the adjacent free point of full point in the board"""   
    
    adjacent = []
    for x in range(MAX_BOARD):
        for y in range(MAX_BOARD):
            if board[x][y] == 0:
                tag = 0
                for x_direction, y_direction in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
                    for step in [1, 2]:
                        _x = x + x_direction*step
                        _y = y + y_direction*step
                        if isCrossing(_x,_y):
                            continue
                        if board[_x][_y] == 0:
                            continue
                        else:
                            tag = 1
                if tag == 1:
                    adjacent.append((x, y))

    if len(adjacent) == 0:
        adjacent.append( (int(MAX_BOARD/2), int(MAX_BOARD/2)) )  
    if shuffle: 
        random.shuffle(adjacent)                    
    return adjacent

def Adjacent4Point(board, point):
    adjacent = set()
    for x_direction, y_direction in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
        for step in [1, 2]:
            x = point[0] + x_direction*step
            y = point[1] + y_direction*step
            if isCrossing(x,y) or (x, y)==point:
                continue
            if board[x][y] == 0:
                adjacent.add( (x, y) )
            
    return adjacent

##############################################################

def count_rest_four_my(board, who):
        '''
        It is the  function that count all sorts of rest four, eg. 'xoooo-', 'xoo-oox ,...
        '''
        if who == 1:
            count = board.pattern_finder.get_pattern_count('xoooo-', board.features) + board.pattern_finder.get_pattern_count('--ooo-o', board.features
            ) + board.pattern_finder.get_pattern_count('x-ooo-o', board.features) + board.pattern_finder.get_pattern_count('xooo-o-', board.features) + board.pattern_finder.get_pattern_count('xoo-oo-', board.features
            ) + board.pattern_finder.get_pattern_count('xooo-oo', board.features) + board.pattern_finder.get_pattern_count('xooo-ox', board.features) + board.pattern_finder.get_pattern_count('xoo-oox', board.features)
        else:
            count = board.pattern_finder.get_pattern_count('oxxxx-', board.features) + board.pattern_finder.get_pattern_count('--xxx-x', board.features
        ) + board.pattern_finder.get_pattern_count('o-xxx-x', board.features) + board.pattern_finder.get_pattern_count('oxxx-x-', board.features) + board.pattern_finder.get_pattern_count('oxx-xx-', board.features
        ) + board.pattern_finder.get_pattern_count('oxxx-xx', board.features) + board.pattern_finder.get_pattern_count('oxxx-xo', board.features) + board.pattern_finder.get_pattern_count('oxx-xxo', board.features)

        return count
    
def count_rest_four_op(board, who):
    '''
    It is the  function that count all sorts of rest four, eg. 'oxxxx-', 'oxx-xxo ,...
    '''
    if who == 1:
        count = board.pattern_finder.get_pattern_count('oxxxx-', board.features) + board.pattern_finder.get_pattern_count('--xxx-x', board.features
    ) + board.pattern_finder.get_pattern_count('o-xxx-x', board.features) + board.pattern_finder.get_pattern_count('oxxx-x-', board.features) + board.pattern_finder.get_pattern_count('oxx-xx-', board.features
    ) + board.pattern_finder.get_pattern_count('oxxx-xx', board.features) + board.pattern_finder.get_pattern_count('oxxx-xo', board.features) + board.pattern_finder.get_pattern_count('oxx-xxo', board.features)            
    else:
        count = board.pattern_finder.get_pattern_count('xoooo-', board.features) + board.pattern_finder.get_pattern_count('--ooo-o', board.features
        ) + board.pattern_finder.get_pattern_count('x-ooo-o', board.features) + board.pattern_finder.get_pattern_count('xooo-o-', board.features) + board.pattern_finder.get_pattern_count('xoo-oo-', board.features
        ) + board.pattern_finder.get_pattern_count('xooo-oo', board.features) + board.pattern_finder.get_pattern_count('xooo-ox', board.features) + board.pattern_finder.get_pattern_count('xoo-oox', board.features)

    return count

def count_live_three_my(board, who):
    '''
    It is the  function that count all sorts of live three, eg. '--ooo--',...
    '''
    if who == 1:
        count = board.pattern_finder.get_pattern_count('--ooo--', board.features) + board.pattern_finder.get_pattern_count('x-ooo--', board.features) + board.pattern_finder.get_pattern_count('-oo-o-', board.features)
    else:
        count = board.pattern_finder.get_pattern_count('--xxx--', board.features) + board.pattern_finder.get_pattern_count('o-xxx--', board.features) + board.pattern_finder.get_pattern_count('-xx-x-', board.features)

    return count

def count_live_three_op(board, who):
    '''
    It is the  function that count all sorts of live three, eg. '--xxx--',...
    '''
    if who == 1:
        count = board.pattern_finder.get_pattern_count('--xxx--', board.features) + board.pattern_finder.get_pattern_count('o-xxx--', board.features) + board.pattern_finder.get_pattern_count('-xx-x-', board.features)
    else:
        count = board.pattern_finder.get_pattern_count('--ooo--', board.features) + board.pattern_finder.get_pattern_count('x-ooo--', board.features) + board.pattern_finder.get_pattern_count('-oo-o-', board.features)

    return count

def count_rest_three_my(board, who):
    '''
    It is the  function that count all sorts of rest three, eg. 'xooo--',...
    '''
    if who == 1:
        count = board.pattern_finder.get_pattern_count('x-ooo-x', board.features) + board.pattern_finder.get_pattern_count('xooo--', board.features) + board.pattern_finder.get_pattern_count('xoo-o--', board.features
    ) + board.pattern_finder.get_pattern_count('xo-oo--', board.features) + board.pattern_finder.get_pattern_count('xo-o-o-', board.features) + board.pattern_finder.get_pattern_count('-o-o-o-', board.features
    ) + board.pattern_finder.get_pattern_count('xo-oo-x', board.features) + board.pattern_finder.get_pattern_count('xoo-o-x', board.features) + board.pattern_finder.get_pattern_count('xo-o-ox', board.features)
    else:
        count = board.pattern_finder.get_pattern_count('o-xxx-o', board.features) + board.pattern_finder.get_pattern_count('oxxx--', board.features) + board.pattern_finder.get_pattern_count('oxx-x--', board.features
    ) + board.pattern_finder.get_pattern_count('ox-xx--', board.features) + board.pattern_finder.get_pattern_count('ox-x-x-', board.features) + board.pattern_finder.get_pattern_count('-x-x-x-', board.features
    ) + board.pattern_finder.get_pattern_count('ox-xx-o', board.features) + board.pattern_finder.get_pattern_count('oxx-x-o', board.features) + board.pattern_finder.get_pattern_count('ox-x-xo', board.features)

    return count

def count_rest_three_op(board, who):
    '''
    It is the  function that count all sorts of rest three, eg. 'oxxx--',...
    '''
    if who == 1:
        count = board.pattern_finder.get_pattern_count('o-xxx-o', board.features) + board.pattern_finder.get_pattern_count('oxxx--', board.features) + board.pattern_finder.get_pattern_count('oxx-x--', board.features
        ) + board.pattern_finder.get_pattern_count('ox-xx--', board.features) + board.pattern_finder.get_pattern_count('ox-x-x-', board.features) + board.pattern_finder.get_pattern_count('-x-x-x-', board.features
        ) + board.pattern_finder.get_pattern_count('ox-xx-o', board.features) + board.pattern_finder.get_pattern_count('oxx-x-o', board.features) + board.pattern_finder.get_pattern_count('ox-x-xo', board.features)
    else:
        count = board.pattern_finder.get_pattern_count('x-ooo-x', board.features) + board.pattern_finder.get_pattern_count('xooo--', board.features) + board.pattern_finder.get_pattern_count('xoo-o--', board.features
    ) + board.pattern_finder.get_pattern_count('xo-oo--', board.features) + board.pattern_finder.get_pattern_count('xo-o-o-', board.features) + board.pattern_finder.get_pattern_count('-o-o-o-', board.features
    ) + board.pattern_finder.get_pattern_count('xo-oo-x', board.features) + board.pattern_finder.get_pattern_count('xoo-o-x', board.features) + board.pattern_finder.get_pattern_count('xo-o-ox', board.features)

    return count

def count_live_four_my(board,who):
    if who == 1:
        count = board.pattern_finder.get_pattern_count('-oooo-', board.features) + board.pattern_finder.get_pattern_count('o-ooo-o', board.features)
    else:
        count = board.pattern_finder.get_pattern_count('-xxxx-', board.features) + board.pattern_finder.get_pattern_count('x-xxx-x', board.features)
    
    return count

def count_live_four_op(board,who):
    if who == 1:
        count = board.pattern_finder.get_pattern_count('-xxxx-', board.features) + board.pattern_finder.get_pattern_count('x-xxx-x', board.features)
    else:
        count = board.pattern_finder.get_pattern_count('-oooo-', board.features) + board.pattern_finder.get_pattern_count('o-ooo-o', board.features)
    
    return count

def count_live_two_op(board, who):
    '''
    It is the  function that count all sorts of live two, eg. '--xx--',...
    '''
    if who == 1:
        count = board.pattern_finder.get_pattern_count('--xx--', board.features) + board.pattern_finder.get_pattern_count('o-xx--', board.features
        ) + board.pattern_finder.get_pattern_count('--x-x--', board.features) + board.pattern_finder.get_pattern_count('o-x-x--', board.features) 
    else:
        count = board.pattern_finder.get_pattern_count('--oo--', board.features) + board.pattern_finder.get_pattern_count('x-oo--', board.features
        ) + board.pattern_finder.get_pattern_count('--o-o--', board.features) + board.pattern_finder.get_pattern_count('x-o-o--', board.features) 

    return count

def heuristic_my(board, who):
    '''
    It is the heuristic function with 10^k increasing rewards.
    The total num of patterns is 1+5+5+3+3+4+3+3+1+1=29
    '''
    factor = 0.90
    heuristic = 0.0
    if who == 1:
        # 10000 1
        heuristic += (board.pattern_finder.get_pattern_count('-oooo-', board.features)) * 10000
        # 1000 5
        heuristic += (board.pattern_finder.get_pattern_count('--ooo--', board.features) + board.pattern_finder.get_pattern_count('xoooo-', board.features) + board.pattern_finder.get_pattern_count('o-ooo-o', board.features) + board.pattern_finder.get_pattern_count('--ooo-o', board.features) + board.pattern_finder.get_pattern_count('x-ooo-o', board.features)) * 1000
        # 1000 * factor 5
        heuristic += (board.pattern_finder.get_pattern_count('x-ooo--', board.features) + board.pattern_finder.get_pattern_count('-oo-o-', board.features) + board.pattern_finder.get_pattern_count('xooo-o-', board.features) + board.pattern_finder.get_pattern_count('xoo-oo-', board.features) + board.pattern_finder.get_pattern_count('xooo-oo', board.features)) * 1000 * factor
        # 1000 * factor * factor 3
        heuristic += (board.pattern_finder.get_pattern_count('x-ooo-x', board.features) + board.pattern_finder.get_pattern_count('xooo-ox', board.features) + board.pattern_finder.get_pattern_count('xoo-oox', board.features)) * 1000 * factor * factor
        # 100 3
        heuristic += (board.pattern_finder.get_pattern_count('--oo--', board.features) + board.pattern_finder.get_pattern_count('-o-o-o-', board.features) + board.pattern_finder.get_pattern_count('xooo--', board.features)) * 100
        # 100 * factor 4
        heuristic += (board.pattern_finder.get_pattern_count('x-oo--', board.features) + board.pattern_finder.get_pattern_count('xoo-o--', board.features) + board.pattern_finder.get_pattern_count('xo-oo--', board.features) + board.pattern_finder.get_pattern_count('xo-o-o-', board.features)) * 100 * factor
        # 100 * factor * factor 3
        heuristic += (board.pattern_finder.get_pattern_count('xo-oo-x', board.features) + board.pattern_finder.get_pattern_count('xoo-o-x', board.features) + board.pattern_finder.get_pattern_count('xo-o-ox', board.features)) * 100 * factor * factor
        # 10 3
        heuristic += (board.pattern_finder.get_pattern_count('--o--', board.features) + board.pattern_finder.get_pattern_count('xoo---', board.features) + board.pattern_finder.get_pattern_count('--o-o--', board.features)) * 10
        # 10 * factor 1
        heuristic += (board.pattern_finder.get_pattern_count('x-o-o--', board.features)) * 10 * factor
        # 10 * factor * factor 1
        heuristic += (board.pattern_finder.get_pattern_count('x-o-o-x', board.features)) * 10 * factor * factor
    else:
        # 10000 1
        heuristic += (board.pattern_finder.get_pattern_count('-xxxx-', board.features)) * 10000
        # 1000 5
        heuristic += (board.pattern_finder.get_pattern_count('--xxx--', board.features) + board.pattern_finder.get_pattern_count('oxxxx-', board.features) + board.pattern_finder.get_pattern_count('x-xxx-x', board.features) + board.pattern_finder.get_pattern_count('--xxx-x', board.features) + board.pattern_finder.get_pattern_count('o-xxx-x', board.features)) * 1000
        # 1000 * factor 5
        heuristic += (board.pattern_finder.get_pattern_count('o-xxx--', board.features) + board.pattern_finder.get_pattern_count('-xx-x-', board.features) + board.pattern_finder.get_pattern_count('oxxx-x-', board.features) + board.pattern_finder.get_pattern_count('oxx-xx-', board.features) + board.pattern_finder.get_pattern_count('oxxx-xx', board.features)) * 1000 * factor
        # 1000 * factor * factor 3
        heuristic += (board.pattern_finder.get_pattern_count('o-xxx-o', board.features) + board.pattern_finder.get_pattern_count('oxxx-xo', board.features) + board.pattern_finder.get_pattern_count('oxx-xxo', board.features)) * 1000 * factor * factor
        # 100 3
        heuristic += (board.pattern_finder.get_pattern_count('--xx--', board.features) + board.pattern_finder.get_pattern_count('-x-x-x-', board.features) + board.pattern_finder.get_pattern_count('oxxx--', board.features)) * 100
        # 100 * factor 4
        heuristic += (board.pattern_finder.get_pattern_count('o-xx--', board.features) + board.pattern_finder.get_pattern_count('oxx-x--', board.features) + board.pattern_finder.get_pattern_count('ox-xx--', board.features) + board.pattern_finder.get_pattern_count('ox-x-x-', board.features)) * 100 * factor
        # 100 * factor * factor 3
        heuristic += (board.pattern_finder.get_pattern_count('ox-xx-o', board.features) + board.pattern_finder.get_pattern_count('oxx-x-o', board.features) + board.pattern_finder.get_pattern_count('ox-x-xo', board.features)) * 100 * factor * factor
        # 10 3
        heuristic += (board.pattern_finder.get_pattern_count('--x--', board.features) + board.pattern_finder.get_pattern_count('oxx---', board.features) + board.pattern_finder.get_pattern_count('--x-x--', board.features)) * 10
        # 10 * factor 1
        heuristic += (board.pattern_finder.get_pattern_count('o-x-x--', board.features)) * 10 * factor
        # 10 * factor * factor 1
        heuristic += (board.pattern_finder.get_pattern_count('o-x-x-o', board.features)) * 10 * factor * factor

    return heuristic


def heuristic_op(board, who):
    '''
    It is the heuristic function with 10^k increasing rewards.
    The total num of patterns is 1+5+5+3+3+4+3+3+1+1=29
    '''
    factor = 0.90
    heuristic = 0.0
    if who == 1:
        # 10000 1
        heuristic += (board.pattern_finder.get_pattern_count('-xxxx-', board.features)) * 10000
        # 1000 5
        heuristic += (board.pattern_finder.get_pattern_count('--xxx--', board.features) + board.pattern_finder.get_pattern_count('oxxxx-', board.features) + board.pattern_finder.get_pattern_count('x-xxx-x', board.features) + board.pattern_finder.get_pattern_count('--xxx-x', board.features) + board.pattern_finder.get_pattern_count('o-xxx-x', board.features)) * 1000
        # 1000 * factor 5
        heuristic += (board.pattern_finder.get_pattern_count('o-xxx--', board.features) + board.pattern_finder.get_pattern_count('-xx-x-', board.features) + board.pattern_finder.get_pattern_count('oxxx-x-', board.features) + board.pattern_finder.get_pattern_count('oxx-xx-', board.features) + board.pattern_finder.get_pattern_count('oxxx-xx', board.features)) * 1000 * factor
        # 1000 * factor * factor 3
        heuristic += (board.pattern_finder.get_pattern_count('o-xxx-o', board.features) + board.pattern_finder.get_pattern_count('oxxx-xo', board.features) + board.pattern_finder.get_pattern_count('oxx-xxo', board.features)) * 1000 * factor * factor
        # 100 3
        heuristic += (board.pattern_finder.get_pattern_count('--xx--', board.features) + board.pattern_finder.get_pattern_count('-x-x-x-', board.features) + board.pattern_finder.get_pattern_count('oxxx--', board.features)) * 100
        # 100 * factor 4
        heuristic += (board.pattern_finder.get_pattern_count('o-xx--', board.features) + board.pattern_finder.get_pattern_count('oxx-x--', board.features) + board.pattern_finder.get_pattern_count('ox-xx--', board.features) + board.pattern_finder.get_pattern_count('ox-x-x-', board.features)) * 100 * factor
        # 100 * factor * factor 3
        heuristic += (board.pattern_finder.get_pattern_count('ox-xx-o', board.features) + board.pattern_finder.get_pattern_count('oxx-x-o', board.features) + board.pattern_finder.get_pattern_count('ox-x-xo', board.features)) * 100 * factor * factor
        # 10 3
        heuristic += (board.pattern_finder.get_pattern_count('--x--', board.features) + board.pattern_finder.get_pattern_count('oxx---', board.features) + board.pattern_finder.get_pattern_count('--x-x--', board.features)) * 10
        # 10 * factor 1
        heuristic += (board.pattern_finder.get_pattern_count('o-x-x--', board.features)) * 10 * factor
        # 10 * factor * factor 1
        heuristic += (board.pattern_finder.get_pattern_count('o-x-x-o', board.features)) * 10 * factor * factor
    else:
        # 10000 1
        heuristic += (board.pattern_finder.get_pattern_count('-oooo-', board.features)) * 10000
        # 1000 5
        heuristic += (board.pattern_finder.get_pattern_count('--ooo--', board.features) + board.pattern_finder.get_pattern_count('xoooo-', board.features) + board.pattern_finder.get_pattern_count('o-ooo-o', board.features) + board.pattern_finder.get_pattern_count('--ooo-o', board.features) + board.pattern_finder.get_pattern_count('x-ooo-o', board.features)) * 1000
        # 1000 * factor 5
        heuristic += (board.pattern_finder.get_pattern_count('x-ooo--', board.features) + board.pattern_finder.get_pattern_count('-oo-o-', board.features) + board.pattern_finder.get_pattern_count('xooo-o-', board.features) + board.pattern_finder.get_pattern_count('xoo-oo-', board.features) + board.pattern_finder.get_pattern_count('xooo-oo', board.features)) * 1000 * factor
        # 1000 * factor * factor 3
        heuristic += (board.pattern_finder.get_pattern_count('x-ooo-x', board.features) + board.pattern_finder.get_pattern_count('xooo-ox', board.features) + board.pattern_finder.get_pattern_count('xoo-oox', board.features)) * 1000 * factor * factor
        # 100 3
        heuristic += (board.pattern_finder.get_pattern_count('--oo--', board.features) + board.pattern_finder.get_pattern_count('-o-o-o-', board.features) + board.pattern_finder.get_pattern_count('xooo--', board.features)) * 100
        # 100 * factor 4
        heuristic += (board.pattern_finder.get_pattern_count('x-oo--', board.features) + board.pattern_finder.get_pattern_count('xoo-o--', board.features) + board.pattern_finder.get_pattern_count('xo-oo--', board.features) + board.pattern_finder.get_pattern_count('xo-o-o-', board.features)) * 100 * factor
        # 100 * factor * factor 3
        heuristic += (board.pattern_finder.get_pattern_count('xo-oo-x', board.features) + board.pattern_finder.get_pattern_count('xoo-o-x', board.features) + board.pattern_finder.get_pattern_count('xo-o-ox', board.features)) * 100 * factor * factor
        # 10 3
        heuristic += (board.pattern_finder.get_pattern_count('--o--', board.features) + board.pattern_finder.get_pattern_count('xoo---', board.features) + board.pattern_finder.get_pattern_count('--o-o--', board.features)) * 10
        # 10 * factor 1
        heuristic += (board.pattern_finder.get_pattern_count('x-o-o--', board.features)) * 10 * factor
        # 10 * factor * factor 1
        heuristic += (board.pattern_finder.get_pattern_count('x-o-o-x', board.features)) * 10 * factor * factor
    
    return heuristic


def heuristic(board, who):
    return heuristic_my(board, who) - 5 *heuristic_op(board, who)