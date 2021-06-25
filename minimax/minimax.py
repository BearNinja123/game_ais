# resource classes for two-player games that have minimax AIs

from tqdm import tqdm
import pickle as pkl
import numpy as np
import random, time, pdb, gc

def logg(*args):
    print(*args)

class State:
    def __init__(self, state=None, parentIsAI=False):
        self.state = state
        self.parentIsAI = parentIsAI

    def update(self, move):
        pass

    def isTerminal(self, depth, maxDepth):
        pass

    def copy(self):
        myClass = type(self)
        return myClass(state=self.state)

    def findState(self, move):
        ret = self.copy()
        ret.update(move)
        return ret

class Node:
    def __init__(self, parentMoveVal=None, state=None, parent=None, parentIsAI=False):
        self.parentMoveVal = parentMoveVal
        self.state = state
        self.parent = parent
        self.parentIsAI = parentIsAI
        self.reward = 0
        self.bestChild = None
        self.children = set()

    def genChildren(self):
        for move in self.listMoves():
            child = type(self)(
                parentMoveVal=move,
                state=self.state.findState(move),
                parent=self,
                parentIsAI = not self.parentIsAI)
            self.children.add(child)

    def listMoves(self): # method implementation varies from game to game
        pass

    def isTerminal(self, depth, maxDepth):
        return self.state.isTerminal(depth, maxDepth)

    def findChild(self, val):
        for child in self.children:
            if child.parentMoveVal == val:
                return child

class Game:
    def __init__(self, state=None):
        self.state = state
        self.turn = True # says that you are going first

    def play(self, val, verbose=True): # returns an int reward, and a None if the game hasn't finished yet
        pass

    def printState(self):
        print(self.state.state)

    def fightAI(self, nodeClass, loadFile=None):
        def inp():
            self.printState()
            return int(input('Enter move: '))

        playerInp = inp()

        if loadFile is None:
            ai = Minimax(type(self), nodeClass, self.state)
        else:
            if not loadFile.endswith('.pkl'):
                loadFile += '.pkl'
            with open(loadFile, 'rb') as infile:
                ai = pkl.load(infile)
                infile.close()
                ai.trials = trialsPerMove

        winner = self.play(playerInp)
        ai.root.state = self.state

        while winner is None:
            aiMoveNode, reward = ai.play(self.state, playerInp)
            aiMove = aiMoveNode.parentMoveVal

            print('AI chooses {} | {} max reward (assuming optimal opponent)'.format(aiMove, reward))
            winner = self.play(aiMove)
            if winner is not None:
                break

            ai.root = aiMoveNode
            logg('Available moves:', ai.root.listMoves())
            playerInp = inp()
            winner = self.play(playerInp)

class Minimax:
    def __init__(self, game, nodeClass, initialState, depth=4):
        self.depth = depth
        self.game = game
        self.nodeClass = nodeClass
        self.root = nodeClass(state=initialState)
        self.root.genChildren()

    def minimax(self, node, depth=0, alpha=-np.inf, beta=np.inf):
        reward = node.isTerminal(depth, self.depth)
        if reward is not None and reward is not False:
            node.reward = reward
        else:
            if len(node.children) == 0:
                node.genChildren()

            for child in node.children:
                self.minimax(child, depth + 1, alpha, beta)

                if node.bestChild is None:
                    node.bestChild = child
                elif node.parentIsAI and child.reward > node.bestChild.reward:
                    node.bestChild = child
                    alpha = child.reward
                    if beta <= alpha:
                        break
                elif (not node.parentIsAI) and child.reward < node.bestChild.reward:
                    node.bestChild = child
                    beta = child.reward
                    if beta <= alpha:
                        break
            node.reward = node.bestChild.reward

    def play(self, state, playerMove=None):
        if playerMove is not None and len(self.root.children) > 0:
            self.root = self.root.findChild(playerMove)
        else:
            self.root = self.nodeClass(parentIsAI=True, state=self.root.state.findState(playerMove))

        if self.root is None:
            self.root = self.nodeClass(parentIsAI=True, state=self.root.state.findState(playerMove))

        if self.root.bestChild is None:
            self.root.parent = None
            gc.collect()
            self.minimax(self.root)

        bestChild = self.root.bestChild

        print('Best Child\'s reward:', bestChild.reward)
        return bestChild, bestChild.reward
