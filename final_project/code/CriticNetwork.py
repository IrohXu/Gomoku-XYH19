from NeuralNetwork import *
from Debug import logDebug
import os
import pickle

class CriticNetwork():
    def __init__(self, params, pattern_finder):
        self.ALPHA = 1
        self.LEARNING_RATE = 0.1
        self.MAGNIFY = 1
        activator = SigmoidActivator()
        self.layers = []
        for i in range(len(params) - 1):
            self.layers.append(FullConnectedLayer(params[i], params[i+1], activator))
        
        self.losing_encodings = [
            pattern_finder.get_encoding('-xxxx'), 
            pattern_finder.get_encoding('x-xxx'), 
            pattern_finder.get_encoding('xx-xx'),
        ]
        self.winning_encodings = [
            pattern_finder.get_encoding('-oooo'), 
            pattern_finder.get_encoding('o-ooo'), 
            pattern_finder.get_encoding('oo-oo'),
        ]

    def load_layers(self, filepath):
        if os.path.exists(filepath):
            self.layers = pickle.load(open(filepath, 'rb'))
            logDebug('Loaded existing model at '+filepath)
        else:
            logDebug('File '+filepath+' does not exist')

    def extract_features(self, board):
        #logDebug('board features: '+ str(board.features))
        flattened_features = []
        for feature in board.features:
            for i in range(4):
                flattened_features.append(int(feature > i))
            flattened_features.append( (feature-4)/2 if feature>4 else 0 )
        return np.asarray(flattened_features + [board.whose_turn-1, 2-board.whose_turn]).reshape(-1, 1)
        #return np.random.rand(200, 1)

    def forward(self, board):
        if board.win is not None:
            return 1 if board.win else 0
        
        if board.whose_turn == 1:
            for index in self.winning_encodings:
                if board.features[index] > 0:
                    return 1
        if board.whose_turn == 2:
            for index in self.losing_encodings:
                if board.features[index] > 0:
                    return 0
        '''
        if board.features[self.winning_encoding] > 0: # 注意！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
            return 0.99
        '''

        output = self.extract_features(board)
        for layer in self.layers:
            layer.forward(output)
            output = layer.output_data
        return float(output)

    def calc_gradient(self, error):
        delta = -self.ALPHA*error #注意！！！
        for layer in self.layers[::-1]:
            delta = layer.backward(delta)
        #return error * delta
        return delta

    def back_propagation(self, board, board_next, reward):
        next_V = self.forward(board_next)
        V = self.forward(board)
        learning_rate = self.LEARNING_RATE*self.MAGNIFY if next_V == 0 else self.LEARNING_RATE
        error = self.ALPHA* (reward + next_V - V)
        logDebug('error: '+str(error))
        self.calc_gradient(error)
        
        for layer in self.layers:
            layer.update(learning_rate, MBGD_mode=0)
        logDebug('value previous: '+str(V))
        logDebug('value updated: '+str(self.forward(board)))