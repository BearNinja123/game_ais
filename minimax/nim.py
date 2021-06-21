# have AI play Nim via minimax

from minimax import *
from tqdm import tqdm
import numpy.random as npr
import numpy as np
import random, time

class NimState(State):
    def __init__(self, state=None):
        super().__init__(state)
        self.parentIsAI = True

    def update(self, move):
        self.state -= move
        self.parentIsAI = not self.parentIsAI

    def isTerminal(self, depth, maxDepth):
        if depth >= maxDepth:
            if self.parentIsAI:
                if self.state % 4 == 0:
                    return 1
                return -1
            else:
                if self.state % 4 == 0:
                    return -1
                return 1

        if self.state <= 0:
            if self.parentIsAI:
                return 1
            return -1
        return None

    def copy(self):
        ret = NimState(state=self.state)
        ret.parentIsAI = self.parentIsAI
        return ret

class NimNode(Node):
    def listMoves(self):
        return set(range(1, min(4, self.state.state+1))) # method implementation varies from game to game

class Nim(Game):
    def __init__(self, numStart=11):
        super().__init__()
        self.statePerm = NimState(numStart)
        self.state = self.statePerm.copy()

    def play(self, val, verbose=True): # returns an int reward
        self.state.update(val)
        ended = self.state.isTerminal(0, 1)
        if ended is not None:
            if self.turn:
                if verbose:
                    print('Player wins')
            else:
                if verbose:
                    print('Player loses')
            return ended
        self.turn = not self.turn
        return None 

    def printState(self):
        print('Current state:', self.state.state)

    def calcReward(node, won):
        winReward = 1
        loseReward = 0

        if (won and node.parentIsAI) or (not won and not node.parentIsAI):
            return winReward
        if (won and not node.parentIsAI) or (not won and node.parentIsAI):
            return loseReward

nim = Nim()
nim.fightAI(NimNode)
