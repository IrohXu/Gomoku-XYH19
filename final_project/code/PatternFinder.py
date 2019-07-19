from Debug import logDebug
class Node():
    def __init__(self, pattern):
        self.pattern = pattern
        self.childs = [None, None, None]

class PatternFinder():
    def __init__(self, patterns):
        self.patterns = patterns
        self._append_switch_side_patterns(patterns)
        self.pattern_tuples = self._append_reverse_patterns(patterns)
        logDebug('Finding Patterns: '+ str(self.pattern_tuples))
        self.pattern_encoding = self._generate_pattern_encoding(self.pattern_tuples)
        logDebug('Pattern encoding: '+ str(self.pattern_encoding))
        self.symbol2boardvalue = {'-': 0, 'o': 1, 'x':2}

        self.root = Node(None) # Unused Head
        for pattern in patterns:
            p = self.root
            for i, symbol in enumerate(pattern):
                is_pattern_end = True if i == len(pattern) - 1 else False
                board_value = self.symbol2boardvalue[symbol]

                if p.childs[board_value] is None:
                    p.childs[board_value] = Node(None)
                if is_pattern_end:
                    p.childs[board_value].pattern = pattern

                p = p.childs[board_value]

    def _append_reverse_patterns(self, patterns):
        pattern_tuples = []
        appended_patterns = []
        for pattern in patterns:
            reversed_pattern = pattern[::-1]
            if reversed_pattern == pattern: # -ooo-
                pattern_tuples.append( [pattern] ) # 不要把这边改成元组！
            elif reversed_pattern not in patterns: # -ooox
                pattern_tuples.append( (pattern, reversed_pattern) )
                appended_patterns.append(reversed_pattern)
            else: # -ooox xooo-
                raise Exception('Repetitive patterns: %s, %s'% (pattern, reversed_pattern))
        self.patterns += appended_patterns
        return pattern_tuples
    def _append_switch_side_patterns(self, patterns):
        switch_side_mapping = {'x':'o', 'o':'x', '-':'-'}
        for pattern in patterns:
            switch_side_pattern = list(pattern)
            for i in range(len(switch_side_pattern)):
                switch_side_pattern[i] = switch_side_mapping[switch_side_pattern[i]]
            switch_side_pattern = ''.join(switch_side_pattern)
            if switch_side_pattern not in patterns:
                patterns.append(switch_side_pattern)
                
    def _generate_pattern_encoding(self, pattern_tuples): # 合并对称等价的patterns
        result = {}
        for i, pattern_tuple in enumerate(pattern_tuples):
            for pattern in pattern_tuple:
                result[pattern] = i
        return result
        #return {patterns[i]: i for i in range(len(patterns)) }

    def get_encoding(self, pattern):
        '''获得某个pattern到feature的list的索引'''
        return self.pattern_encoding[pattern]

    def get_pattern_count(self, pattern, count_list):
        return count_list[self.get_encoding(pattern)]

    def find(self, board_value_lists):
        result = [0 for i in range(len(self.pattern_encoding))]
        for board_value_list in board_value_lists:
            for start_pos in range(len(board_value_list)):
                p = self.root
                for i in range(start_pos, len(board_value_list)):
                    board_value = board_value_list[i]
                    p = p.childs[board_value]
                    if p is None:
                        break # 改变 start_pos 进行下一次匹配
                    if p.pattern is not None:
                        result[self.pattern_encoding[p.pattern]] += 1
        return result

if __name__ == '__main__':
    feature_patterns = [
                '-oooo-', 'oo-oo', 'o-ooo', '-oooo', 
                '--ooo-', '-o-oo-', 'xo-oo-', 'xoo-o-', 'xooo--', 'oo--o',
                'o---o', '-oo--', '-o-o--', '-o--o-',
                '-o----',
            ]
    pattern_finder = PatternFinder(feature_patterns)
    print(pattern_finder.pattern_encoding)