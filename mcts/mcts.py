# resource classes for two-player games that have MCTS AIs

from tqdm import tqdm
import pickle as pkl
import numpy.random as npr
import numpy as np
import random, time, pdb

def logg(*args):
    print(*args)

class State:
    def __init__(self, state=None, parentIsAI=False):
        self.state = state
        self.parentIsAI = parentIsAI

    def update(self, move):
        pass

    def isTerminal(self):
        pass

    def copy(self):
        myClass = type(self)
        return myClass(state=self.state)

    def findState(move, currentState): # tells how a move affects a state of the game, i.e. a move of 3 with 11 as the currentState will yield 8
        stateCopy = currentState.copy()
        stateCopy.update(move)
        return stateCopy

class Node:
    def __init__(self, parentMoveVal=None, state=None, parent=None, children=set(), parentIsAI=False):
        self.wins = 0
        self.plays = 0
        self.ucb = 0
        self.ucbUpdated = False
        self.parentMoveVal = parentMoveVal
        self.state = state
        self.children = children
        self.parent = parent
        self.parentIsAI = parentIsAI

    def listMoves(self): # method implementation varies from game to game
        pass

    def copy(self):
        ret = type(self)()
        ret.wins = self.wins
        ret.plays = self.plays
        ret.ucb = self.ucb
        ret.ucbUpdated = self.ucbUpdated
        ret.parentMoveVal = self.parentMoveVal
        ret.state = self.state.copy()
        ret.children = self.children
        ret.parent = self.parent
        ret.parentIsAI = self.parentIsAI
        return ret

    def calcUCB(self, c=2**0.5):
        if not self.ucbUpdated:
            self.ucb = self.wins / self.plays + c * (np.log(self.parent.plays) / self.plays) ** 0.5
            self.ucbUpdated = True
        return self.ucb

    def isTerminal(self):
        return self.state.isTerminal()

    def isLeaf(self):
        return len(self.children) != len(self.listMoves())

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

    def calcReward(node, outcome): # function favoring AI - if AI wins return some positive number
        return self.state.isTerminal()

    def printState(self):
        print(self.state.state)

    def simulate(node):
        nodeClass = type(node)
        temp = node.copy()
        tempState = temp.state

        ended = temp.isTerminal()
        while ended is None:
            move = random.sample(temp.listMoves(), 1)[0]
            tempState.update(move)
            temp.parentIsAI = not temp.parentIsAI
            ended = temp.isTerminal()
        return ended

    def fightAI(self, nodeClass, loadFile=None, trialsPerMove=10):
        if loadFile is None:
            ai = MCTS(type(self), nodeClass)
        else:
            if not loadFile.endswith('.pkl'):
                loadFile += '.pkl'
            with open(loadFile, 'rb') as infile:
                ai = pkl.load(infile)
                infile.close()
                ai.trials = trialsPerMove

        def inp():
            self.printState()
            return int(input('Enter move: '))

        playerInp = inp()
        winner = self.play(playerInp)
        ai.root.state = self.state

        while winner is None:
            aiMoveNode, confidence = ai.play(self.state, playerInp)
            aiMove = aiMoveNode.parentMoveVal

            print('AI chooses {} | {}% confidence in AI win'.format(aiMove, round(confidence * 100, 2)))
            winner = self.play(aiMove)
            if winner is not None:
                break

            ai.root = aiMoveNode
            playerInp = inp()
            winner = self.play(playerInp)

    def saveAI(self, nodeClass, saveFile, loadFile=None, trialsPretrain=int(1e4), aiPlaysFirst=False):
        if loadFile is None:
            ai = MCTS(type(self), nodeClass, trialsPerMove=trialsPretrain)
        else:
            if not loadFile.endswith('.pkl'):
                loadFile += '.pkl'
            with open(loadFile, 'rb') as infile:
                ai = pkl.load(infile)
                ai.trials = trialsPretrain
                infile.close()

        ai.root.parentIsAI = aiPlaysFirst

        _, _ = ai.play(self.state, None) # we just want to save the game tree, we don't want to play any moves so the return values don't matter

        if not saveFile.endswith('.pkl'):
            saveFile += '.pkl'
        with open(saveFile, 'wb') as outfile:
            pkl.dump(ai, outfile)
            outfile.close()

class MCTS:
    def __init__(self, game, nodeClass, trialsPerMove=1000):
        self.trials = trialsPerMove
        self.game = game
        self.nodeClass = nodeClass
        self.root = nodeClass()

    def select(self):
        bestNode = self.root
        while not bestNode.isLeaf():
            bestChild = None
            bestUCB = 0
            for child in bestNode.children:
                ucbVal = child.calcUCB()
                if ucbVal > bestUCB or bestChild is None:
                    bestChild = child
                    bestUCB = ucbVal
            if bestChild is None:
                self.backprop(bestNode, bestNode.isTerminal())
                return None
            ended = bestChild.state.isTerminal()
            if ended is not None:
                self.backprop(bestChild, ended)
                return None

            bestNode = bestChild
        return bestNode

    def expand(self, node): # do a simulation to all children of a node if none are visited
        childMoves = set()
        for child in node.children:
            childMoves.add(child.parentMoveVal)

        validMoves = node.listMoves() - childMoves
        newMove = random.sample(validMoves, 1)[0]
        
        stateClass = type(self.root.state)
        child = self.nodeClass(newMove, state=stateClass.findState(newMove, node.state), parent=node, children=set(), parentIsAI=(not node.parentIsAI))
        node.children.add(child)
        return child

    def backprop(self, node, won):
        while node is not None:
            outcome = self.game.calcReward(node, won)
            node.wins += outcome
            node.plays += 1
            node.ucbUpdated = False
            node = node.parent

    def play(self, state, playerMove=None):
        if playerMove is not None and len(self.root.children) > 0:
            self.root = self.root.findChild(playerMove)
            #self.root = self.nodeClass(state=state, children=set())
        if self.root is None:
            self.root = self.nodeClass(state=state, children=set())

        times = {'select': 0, 'expand': 0, 'simulate': 0, 'backprop': 0}
        for i in tqdm(range(self.trials)):
            start = time.time()
            bestNode = self.select()
            times['select'] += time.time() - start
            if type(bestNode) is self.nodeClass:
                start = time.time()
                child = self.expand(bestNode)
                times['expand'] += time.time() - start

                start = time.time()
                won = self.game.simulate(child)
                times['simulate'] += time.time() - start

                start = time.time()
                self.backprop(child, won)
                times['backprop'] += time.time() - start
        print(times)

        bestChild = None
        bestWinRatio = 0

        for child in self.root.children:
            winRatio = child.wins / child.plays
            if bestChild is None or winRatio > bestWinRatio:
                bestChild = child
                bestWinRatio = winRatio

        print('Best Child\'s number of plays:', bestChild.plays)
        return bestChild, bestWinRatio
