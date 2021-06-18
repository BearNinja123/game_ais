# play tic tac toe

from mcts import *
import numpy as np
import random

length = 3

class TTTState(State):
    def __init__(self, state=None):
        self.length = length
        if state is None:
            self.state = np.zeros((self.length, self.length)).astype(np.int8)
        else:
            self.state = state
        self.x = True

    def update(self, move):
        y, x = move // self.length, move % self.length

        assert self.state[y][x] == 0

        if self.x:
            self.state[y][x] = -1
        else:
            self.state[y][x] = 1

        self.x = not self.x

    def isTerminal(self):
        for idx, row in enumerate(self.state):
            if np.abs(np.sum(row)) == self.length:
                return row[0]
            col = self.state[:, idx]
            if np.abs(np.sum(col)) == self.length:
                return col[0]

        lDiag = True
        rDiag = True
        '''for i in range(self.state.shape[0]):
            if self.state[i][i] != self.state[0][0] or self.state[0][0] == 0:
                lDiag = False
            if self.state[-i - 1][i] != self.state[-1][0] or self.state[-1][0] == 0:
                rDiag = False'''
        if not ((self.state[0][0] == self.state[1][1] == self.state[2][2]) and self.state[0][0] != 0):
            lDiag = False
        if not ((self.state[2][0] == self.state[1][1] == self.state[0][2]) and self.state[2][0] != 0):
            rDiag = False
        if lDiag:
            return self.state[0][0]
        if rDiag:
            return self.state[self.state.shape[0] - 1][0]
        if 0 not in self.state:
            return 0
        return None

    def copy(self):
        myClass = type(self)
        ret = myClass(state=np.array(self.state, copy=True))
        ret.x = self.x
        return ret

class TTTNode(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.state is None:
            self.state = TTTState()
        self.state.x = self.parentIsAI

    def listMoves(self): # method implementation varies from game to game
        ys, xs = np.where(self.state.state == 0) # for [[0, 1], [1, 0]], np.where(arr == 0) returns [0, 1] (y-indices), [0, 1] (corresponding x-indices)
        ret = set(ys * self.state.state.shape[0] + xs)
        return ret

class TTT(Game):
    def __init__(self, state=None):
        super().__init__()
        self.state = TTTState()
        self.signs = {0: ' ', -1: 'X', 1: 'O'}
        self.length = length

    def play(self, val, verbose=True): # returns an int reward, and a None if the game hasn't finished yet
        self.state.update(val)
        ended = self.state.isTerminal()
        if ended is not None:
            if ended == 1:
                print('O wins')
            elif ended == -1:
                print('X wins')
            else:
                print('Tie')
            return ended 
        #self.turn = not self.turn
        return None 

    def calcReward(node, outcome): # function favoring AI - if AI wins return some positive number
        if node.parentIsAI: # if a player node finds out its state is terminal before making a move, its parent (an AI node) made a winning move
            return outcome
        else:
            return -outcome

    def printState(self):
        self.printTemp()
        lmo = self.length - 1 # length minus one
        for idx, row in enumerate(self.state.state):
            for elemIdx in range(lmo):
                print('   |', end='')
            print()
            for elemIdx in range(lmo):
                print(' {} |'.format(self.signs[row[elemIdx]]), end='')
            print(' {} '.format(self.signs[row[-1]]))
            if idx != lmo:
                for elemIdx in range(lmo):
                    print('___|', end='')
                print('___')

    '''def play(self, x, y, verbose=True):
        assert self.state[y][x] == 0

        if self.x:
            self.state[y][x] = -1
        else:
            self.state[y][x] = 1

        if verbose:
            self.printBoard()

        self.x = not self.x
        return self.isTerminal()'''

    def printTemp(self):
        '''print('---------------\n',
        '   |   |   \n',
        ' 0 | 1 | 2 \n',
        '___|___|___\n',
        '   |   |   \n',
        ' 3 | 4 | 5 \n',
        '___|___|___\n',
        '   |   |   \n',
        ' 6 | 7 | 8 \n',
        '   |   |   \n',
        '---------------');'''
        print('------------------------------------')
        lmo = self.length - 1 # length minus one
        for idx, row in enumerate(self.state.state):
            for elemIdx in range(lmo):
                print('   |', end='')
            print()
            for elemIdx in range(lmo):
                print(' {} |'.format(idx * self.length + elemIdx), end='')
            print(' {} '.format(idx * self.length + lmo))
            if idx != lmo:
                for elemIdx in range(lmo):
                    print('___|', end='')
                print('___')
        print('------------------------------------')

trialsPretrain = int(1e6)
ttt = TTT()
#ttt.saveAI(TTTNode, 'ttt.pkl', 'ttt.pkl', trialsPretrain=trialsPretrain)
ttt.saveAI(TTTNode, 'ttt.pkl', trialsPretrain=trialsPretrain)
#ttt.fightAI(TTTNode)
ttt.fightAI(TTTNode, 'ttt.pkl')
