# have AI play Nim via a Monte Carlo Tree Search (MCTS)

from mcts import *
from tqdm import tqdm
import numpy.random as npr
import numpy as np
import random, time

class NimState(State):
    def __init__(self, state=None):
        super().__init__(state)
        self.isAI = False

    def update(self, move):
        self.state -= move
        self.isAI = not self.isAI

    def isTerminal(self):
        if self.state <= 0:
            if self.isAI:
                return 1
            return -1
        return None

class NimNode(Node):
    def listMoves(self):
        return set(range(1, min(4, self.state.state+1))) # method implementation varies from game to game

    def isTerminal(self):
        if self.state.state <= 0:
            if self.parentIsAI:
                return 1
            return 0
        return None

class Nim(Game):
    def __init__(self, numStart=24):
        super().__init__()
        self.statePerm = NimState(numStart)
        self.state = self.statePerm

    def play(self, val, verbose=True): # returns an int reward
        self.state.update(val)
        ended = self.state.isTerminal()
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
        print(self.state.state)

    def calcReward(node, won):
        winReward = 1
        loseReward = 0

        if (won and node.parentIsAI) or (not won and not node.parentIsAI):
            return winReward
        if (won and not node.parentIsAI) or (not won and node.parentIsAI):
            return loseReward

nim = Nim()
nim.fightAI(NimNode)
