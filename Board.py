from PatternFinder import PatternFinder
from board_info_helper import check_win, generate_board_value_lists, Adjacent4Point
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
                'x-ooo-x','x-ooo--','--ooo--','--ooo-o','o-ooo-o','x-ooo-o',
                '--oo--','x-oo--',
                'xoo-o--','xo-oo--','xo-oo-x','xoo-o-x',
                'xooo--', 'xoo---',
                'xoooo-',
                '-oo-o-',
                'xooo-o-','xoo-oo-','xooo-ox','xoo-oox','xooo-oo',
                '-o-o-o-','xo-o-ox','xo-o-o-',
                '--o-o--','x-o-o--','x-o-o-x',
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
        self.num_steps = 0
    
    def deepcopy(self):
        board_copy = Board(self.MAX_BOARD, self.pattern_finder)
        board_copy.board = []
        for row in self.board:
            board_copy.board.append(row.copy(board_copy))
        board_copy.features = copy(self.features)
        board_copy.win = self.win
        board_copy.whose_turn = self.whose_turn
        board_copy.num_steps = self.num_steps
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

        for i in range(len(self.pattern_finder.pattern_encoding)):
            self.features[i] += new_features[i] - old_features[i]
        

        if self.win is None and check_win(self, x, y, who):
            self.win = (who == 1)


        if who == 0: # 撤回上一步
            self.whose_turn = 1 if self.whose_turn == 2 else 2
            self.num_steps -= 1
        else:
            self.whose_turn = 1 if who == 2 else 2
            self.num_steps += 1
        

    def print(self, marks=[]):
        for i in range(self.MAX_BOARD):
            for j in range(self.MAX_BOARD):
                if (i, j) in marks:
                    sys.stdout.write('*')
                    continue
                if self.board[i][j] == 0:
                    sys.stdout.write('-')
                elif self.board[i][j] == 1:
                    sys.stdout.write('o')
                elif self.board[i][j] == 2:
                    sys.stdout.write('x')
                else:
                    sys.stdout.write('*')
            sys.stdout.write('\n')
        sys.stdout.write('\n')
        sys.stdout.flush()
    def __str__(self):
        s = ''
        for i in range(self.MAX_BOARD):
            for j in range(self.MAX_BOARD):
                if self.board[i][j] == 0:
                    s += '-'
                elif self.board[i][j] == 1:
                    s += 'o'
                elif self.board[i][j] == 2:
                    s += 'x'
                else:
                    s += '*'
            s += '\n'
        s += '\n'
        return s

    def load(self, filename, whose_turn):
        f = open(filename, 'r')
        for line in f.readlines():
            start = line.index('[')
            end = line.index(']')+1
            where = eval(line[start:end])
            self[where[0]][where[1]] = whose_turn
            whose_turn = 1 if whose_turn==2 else 2


if __name__ == '__main__':
    board = Board(20)
    board_copy = board.deepcopy()
    board_copy[0][0] = 1
    pass