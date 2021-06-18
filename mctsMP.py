# have AI play Nim via a Monte Carlo Tree Search (MCTS)

from multiprocessing import Process, Queue, cpu_count
from tqdm import tqdm
import numpy.random as npr
import numpy as np
import random, time

def logg(val):
    print(val)

class Nim:
    def __init__(self, numStart=31):
        self.numPerm = numStart
        self.num = numStart
        self.turn = True # says that you are going first

    def play(self, val, verbose=True): # returns an int reward
        self.num -= val
        if self.num <= 0:
            self.num = self.numPerm
            if self.turn:
                if verbose:
                    print('Player wins')
                return 0
            else:
                if verbose:
                    print('Player loses')
                return 1
        self.turn = not self.turn
        return -1

    def findState(moveVal, currentState): # tells how a move affects a state of the game, i.e. a move of 3 with 11 as the currentState will yield 8
        return currentState - moveVal

    def simulate(node):
        temp = node
        tempState = temp.state
        ##logg('State',tempState)
        while tempState > 0:
            move = random.sample(temp.listMoves(), 1)[0]
            tempState -= move
            temp = Node(state=tempState, isAI=not temp.isAI)
            ##logg('Move:', move, tempState)
        if temp.isAI:
            return True
        return False

    def calcReward(node, won):
        winReward = 1
        loseReward = 0

        if (won and node.isAI) or (not won and not node.isAI):
            return winReward
        if (won and not node.isAI) or (not won and node.isAI):
            return loseReward

class Node:
    def __init__(self, moveVal=None, state=None, parent=None, children=set(), isAI=True):
        self.wins = 0
        self.plays = 0
        self.moveVal = moveVal
        self.state = state
        self.children = children
        self.parent = parent
        self.isAI = isAI

    def listMoves(self):
        return set(range(1, min(4, self.state+1))) # method implementation varies from game to game

    def isLeaf(self):
        return len(self.children) != len(self.listMoves())

    def findChild(self, val):
        for child in self.children:
            if child.moveVal == val:
                return child

class MCTS:
    def __init__(self, game=Nim, trialsPerMove=100000):
        self.trials = trialsPerMove
        self.game = game
        self.root = Node()

    def ucb(self, wins, numSim, numSimParent, c=2**0.5):
        return wins / numSim + c * (np.log(numSimParent) / numSim) ** 0.5

    def select(self):
        bestNode = self.root
        while not bestNode.isLeaf():
            #logg(bestNode.children, bestNode.listMoves())
            #logg(bestNode, bestNode.children)
            bestChild = None
            bestUCB = 0
            for child in bestNode.children:
                childIsAI = child.isAI
                ucbVal = self.ucb(child.wins, child.plays, bestNode.plays)
                #logg('Move: {} | Wins: {} | Plays: {} | Parent\'s Plays: {}'.format(child.moveVal, child.wins, child.plays, bestNode.plays))
                if bestUCB < ucbVal or bestChild is None:
                    bestChild = child
                    bestUCB = ucbVal
            if bestChild is None:
                if bestNode.isAI:
                    self.backprop(bestNode, True)
                else:
                    self.backprop(bestNode, False)

                return None

            bestNode = bestChild

            ##logg(bestNode)
        
        return bestNode

    def expand(self, node): # do a simulation to all children of a node if none are visited
        ##logg('called')
        newMove = None
        childMoves = set()
        for child in node.children:
            childMoves.add(child.moveVal)

        nodeMoves = node.listMoves()
        for move in nodeMoves:
            if move not in childMoves:
                newMove = move
                break

        ##logg(newMove)
        child = Node(newMove, state=self.game.findState(newMove, node.state), parent=node, children=set(), isAI=(not node.isAI))
        ##logg('Child\'s children', child.children)
        node.children.add(child)
        #outcome = self.game.calcReward(child, self.game.simulate(child, not child.isAI))
        won = self.game.simulate(child)
        ##logg('Child', newMove, outcome)
        self.backprop(child, won)

    def backprop(self, node, won):
        while node is not None:
            outcome = self.game.calcReward(node, won)
            node.wins += outcome
            node.plays += 1
            node = node.parent

    def play(self, state, queue=None, playerMove=None):
        self.root = Node(state=state, children=set())

        for i in tqdm(range(self.trials)):
            bestNode = self.select()
            if type(bestNode) is Node:
                self.expand(bestNode)

        bestChild = None
        bestWinRatio = 0

        ret = {}
        for child in self.root.children:
            winRatio = child.wins / child.plays
            ret[child.moveVal] = winRatio

        if queue is None:
            return ret
        else:
            queue.put(ret)
            #queue.put('a')

nCores = cpu_count()
Q = Queue()

def fight():
    nim = Nim()
    ai = MCTS()
    inp = lambda: int(input('Board State: {} | Choose number (1-3): '.format(nim.num)))
    playerInp = inp()
    winner = nim.play(playerInp)

    while winner == -1:
        # non-multiprocessing
        #aiMove, confidence = ai.play(nim.num)

        # multiprocessing
        procs = []
        for core in range(nCores):
            p = Process(target=ai.play, args=(nim.num, Q, playerInp))
            procs.append(p)
            p.start()

        summative = {}
        for proc in procs:
            proc.join()

            ret = Q.get()
            for key, val in ret.items():
                if key in summative:
                    summative[key] += val
                else:
                    summative[key] = val

        bestMove = None
        bestWinRatio = 0
        for move, winRatio in summative.items():
            if bestWinRatio < winRatio or bestMove is None:
                bestMove = move
                bestWinRatio = winRatio

        aiMove = bestMove
        confidence = bestWinRatio / nCores 

        print('AI chooses {} | {}% confidence in AI win'.format(aiMove, round(confidence * 100, 2)))
        winner = nim.play(aiMove)
        if winner != -1:
            break

        playerInp = inp()
        winner = nim.play(playerInp)

fight()
