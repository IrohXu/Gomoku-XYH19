from board_info_helper import *
from Board import Board


def heuristic_pruning(board, adjacent):
        '''
        返回一个元祖([], int):  (avaliable, win)
        '''
        pruning = []
        inital_two_total = count_live_two_op(board, board.whose_turn) + count_live_three_op(board, board.whose_turn) 
        #逐个adjacent遍历，进行剪枝
        for (x,y) in adjacent:
            who = board.whose_turn
            # 如果下完这一步直接五连
            if check_win(board, x, y, who):
                pruning = [(x, y)]
                return pruning

        #逐个adjacent遍历，进行剪枝
        for (x,y) in adjacent:
            temp_board = board.deepcopy()
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

MAX_BOARD = 20
board = Board(MAX_BOARD)

board.load('history5.txt', 2)
board[5][2] = 2
board[2][4] = 2

board.print()
pruned = heuristic_pruning(board, Adjacent(board))
#pruned = heuristic_pruning(board, [(10, 11), (9, 9)] )
print(pruned)
x, y = pruned[0]
board[x][y] = 1
board.print()

        
