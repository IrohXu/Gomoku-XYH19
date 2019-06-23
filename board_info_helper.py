import random
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
                for i in range(-1, 2, 1):
                    for j in range(-1, 2, 1):
                        if isCrossing(x+i,y+j):
                            continue
                        if board[x+i][y+j] == 0:
                            continue
                        else:
                            tag = 1
                if tag == 1:
                    adjacent.append((x,y))
    if len(adjacent) == 0:
        adjacent.append( (int(MAX_BOARD/2), int(MAX_BOARD/2)) )  
    if shuffle: 
        random.shuffle(adjacent)                    
    return adjacent