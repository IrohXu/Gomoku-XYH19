from PatternFinder import PatternFinder
from board_info_helper import check_win, generate_board_value_lists
from copy import deepcopy, copy
import sys

class Row(object):
    def __init__(self, board, row_number):
        self.row = [0 for j in range(board.MAX_BOARD)]
        self.board = board
        self.row_number = row_number
    def __getitem__(self, j):
        return self.row[j]
    def __setitem__(self, j, value):
        self.board.update_features([self.row_number, j], value)
        self.row[j] = value

    def copy(self, board):
        row_copy = Row(board, self.row_number)
        row_copy.row = copy(self.row)
        return row_copy

        

class Board(object):
    def __init__(self, MAX_BOARD, pattern_finder=None):
        if pattern_finder is None:
            '''
            feature_patterns = [
                '-oooo-', 'oo-oo', 'o-ooo', '-oooo', 
                '--ooo-', '-o-oo-', 'xo-oo-', 'xoo-o-', 'xooo--', 'oo--o',
                'o---o', '-oo--', '-o-o--', '-o--o-',
                '-o----',
            ]
            '''
            feature_patterns = [
                '-oooo-', 
                'x-ooo-x', '--ooo--', 'x-ooo--', 
                'xoooo-', 
                '-oo-o-', 
                'xoo-o-', 'xo-oo-', 
                'xooo-o', 'xoo-oo', 'xo-ooo', 
                'xooo--', 
                '-o-o-o-', 'xo-o-ox', 'xo-o-o-', 
                '--o-o--', 'x-o-o--', 'x-o-o-x', 
                '--oo--', 'x-oo--', 
                '--o--', 

                '-oooo', 'o-ooo', 'oo-oo', 

            ]

            self.pattern_finder = PatternFinder(feature_patterns)
        else:
            self.pattern_finder = pattern_finder
        self.MAX_BOARD = MAX_BOARD
        self.reset()

    def reset(self):
        self.board = [Row(self, i) for i in range(self.MAX_BOARD)]
        self.features = [0 for i in range(len(self.pattern_finder.pattern_encoding))]
        self.win = None
        self.whose_turn = None
    
    def deepcopy(self):
        board_copy = Board(self.MAX_BOARD, self.pattern_finder)
        board_copy.board = []
        for row in self.board:
            board_copy.board.append(row.copy(board_copy))
        board_copy.features = copy(self.features)
        board_copy.win = self.win
        board_copy.whose_turn = self.whose_turn
        return board_copy

    def __getitem__(self, i):
        return self.board[i]
    '''
    def __getattribute__(self, key):
        if key == 'whose_turn':
            if object.__getattribute__(self, key) is None:
    '''

    def update_features(self, action, who):
        x, y = action

        old_board_value_lists, new_board_value_lists = generate_board_value_lists(self, x, y, who)
        old_features = self.pattern_finder.find(old_board_value_lists)
        new_features = self.pattern_finder.find(new_board_value_lists)

        for i in range(len(self.features)):
            self.features[i] += new_features[i] - old_features[i]
        

        if check_win(self, x, y, who):
            self.win = (who == 1)


        if who == 0:
            self.whose_turn = 1 if self.whose_turn == 2 else 2
        else:
            self.whose_turn = 1 if who == 2 else 2

    def print(self):
        for i in range(self.MAX_BOARD):
            for j in range(self.MAX_BOARD):
                if self.board[i][j] == 0:
                    sys.stdout.write('-')
                elif self.board[i][j] == 1:
                    sys.stdout.write('o')
                else:
                    sys.stdout.write('x')
            sys.stdout.write('\n')
        sys.stdout.write('\n')
        sys.stdout.flush()

    