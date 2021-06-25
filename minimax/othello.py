from minimax import *
import numpy as np
import random, pdb

boardLen = 8
mid = boardLen // 2
signs = {0: '.', -1: '++', 1: 'oo'}
readableSigns = {0: '.', -1: '+', 1: 'o'}
neighbors = {(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)}

class OthState(State):
    def __init__(self, state=None, parentIsAI=False):
        super().__init__(parentIsAI=parentIsAI)
        if self.state is None:
            self.state = np.zeros((boardLen, boardLen)).astype(np.int8)
            self.state[mid-1:mid+1, mid-1:mid+1] = np.array([[1, -1], [-1, 1]])

            self.blackPos = {(mid-1, mid), (mid, mid-1)}
            self.whitePos = {(mid-1, mid-1), (mid, mid)}

    def update(self, move):
        if move == -1:
            self.parentIsAI = not self.parentIsAI
            return

        y, x = move // boardLen, move % boardLen
        assert self.state[y][x] == 0

        if self.parentIsAI:
            self.state[y][x] = 1
            self.whitePos.add((y, x))
        else:
            self.state[y][x] = -1
            self.blackPos.add((y, x))

        movePatch = set()
        for stepY, stepX in neighbors:
            if self.check(y, x, stepY, stepX):
                self.fill(y, x, stepY, stepX)

        self.parentIsAI = not self.parentIsAI

    def isTerminal(self, depth, maxDepth):
        numBlacks = len(self.blackPos)
        numWhites = len(self.whitePos)

        if depth >= maxDepth:
            #return (numWhites - numBlacks) / boardLen ** 2
            return self.evalPieces()

        if numBlacks == 0:
            return 999
        if numWhites == 0:
            return -999

        if np.sum(np.abs(self.state)) == boardLen ** 2 or self.listMoves(False) == self.listMoves(True) == {-1,}:
            return 999 * np.sign(numWhites - numBlacks).astype(np.int8)
        return None

    def copy(self):
        ret = OthState()
        ret.state = np.array(self.state, copy=True)
        ret.parentIsAI = self.parentIsAI
        ret.blackPos = self.blackPos.copy()
        ret.whitePos = self.whitePos.copy()
        return ret

    def coordToMove(moveList):
        ret = set()
        for move in moveList:
            y, x = move
            ret.add(y * boardLen + x)
        return ret

    def whatsMyMoves(self, parentIsAI=None):
        if parentIsAI is None:
            parentIsAI = self.parentIsAI

        if parentIsAI:
            myMoves = self.whitePos
            oppMoves = self.blackPos
        else:
            myMoves = self.blackPos
            oppMoves = self.whitePos

        return myMoves, oppMoves

    def check(self, y, x, stepY, stepX, parentIsAI=None): # checks if a player's token is by the direction starting from (x, y) with slope=stepY/stepX with opposing tokens between
        myMoves, oppMoves = self.whatsMyMoves(parentIsAI)

        y += stepY
        x += stepX
        while 0 <= y < boardLen and 0 <= x < boardLen and (y, x) in oppMoves:
            y += stepY
            x += stepX
        if (y, x) in myMoves:
            return True

    def fill(self, y, x, stepY, stepX): # checks if a player's token is by the direction starting from (x, y) with slope=stepY/stepX
        if self.parentIsAI:
            myMoves = self.whitePos
            oppMoves = self.blackPos
        else:
            myMoves = self.blackPos
            oppMoves = self.whitePos

        y += stepY
        x += stepX
        while (y, x) in oppMoves:
            oppMoves.remove((y, x))
            myMoves.add((y, x))
            self.state[y][x] *= -1
            y += stepY
            x += stepX

    def evalPieces(self, parentIsAI=None):
        myMoves, oppMoves = self.whatsMyMoves(parentIsAI)
        adjVal = lambda x: (mid - x) if x < mid else (x - mid + 1)
        addVal = lambda x: (2 ** x) if x % 2 == 0 else -(2 ** x) # the most neg. value will be -2 since -(3 * 2/3) = -2

        myMoveAccum = 0
        for y, x in myMoves:
            y = adjVal(y)
            x = adjVal(x)
            myMoveAccum += addVal(y)
            myMoveAccum += addVal(x)

        oppMoveAccum = 0
        for y, x in oppMoves:
            y = adjVal(y)
            x = adjVal(x)
            oppMoveAccum += addVal(y)
            oppMoveAccum += addVal(x)

        mobility = len(self.listMoves(parentIsAI)) - len(self.listMoves(not parentIsAI))

        return ((myMoveAccum - oppMoveAccum) / boardLen ** 2) + (mobility * 0.25)

    def listMoves(self, parentIsAI=None): # method implementation varies from game to game
        myMoves, oppMoves = self.whatsMyMoves(parentIsAI)

        def genPatch(y, x):
            movePatch = set()
            for stepY, stepX in neighbors:
                if self.check(y-stepY, x-stepX, stepY, stepX, parentIsAI):
                    if not((y-stepY) >= boardLen or (y-stepY) < 0 or (x-stepX) >= boardLen or (x-stepX) < 0):
                        movePatch.add((y-stepY, x-stepX))
            return movePatch

        validMoves = set()
        for move in oppMoves:
            y, x = move
            movePatch = genPatch(y, x)
            surroundMoves = movePatch - self.blackPos - self.whitePos # moves that surround a tile that may be captured
            validMoves = validMoves | surroundMoves

        if len(validMoves) > 0:
            return OthState.coordToMove(validMoves)
        else:
            return {-1,}

class OthNode(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.state is None:
            self.state = OthState()
        self.parentIsAI = self.state.parentIsAI

    def listMoves(self): # method implementation varies from game to game
        return self.state.listMoves()

class Othello(Game):
    def __init__(self, state=None):
        self.state = OthState()
        self.turn = True # says that you are going first

    def play(self, val, verbose=True): # returns an int reward, and a None if the game hasn't finished yet
        self.state.update(val)
        ended = self.state.isTerminal(0, 1)
        if ended is not None and ended is not False:
            print('Final state')
            self.printState()
            if ended == 999:
                print('Whites (oo) wins')
            elif ended == -999:
                print('Blacks (++) wins')
            else:
                print('Tie')
            return ended 
        #self.turn = not self.turn
        return None 

    def calcReward(node, outcome): # function favoring AI - if AI wins return some positive number
        pass

    def printState(self):
        def pad(s, length=2):
            s = str(s)
            for i in range(length - len(str(s))):
                s += ' '
            return s

        def processRow(row, rowIdx):
            ret = []
            for idx, elem in enumerate(row):
                if elem != 0:
                    ret.append(pad(signs[elem]))
                else:
                    ret.append(pad(idx + boardLen * rowIdx))
                    #ret.append(pad(''))

            return ret

        for _ in range(5 * boardLen):
            print('_', end='')
        print('_')

        for rowIdx, row in enumerate(self.state.state):
            for _ in range(boardLen):
                print('|    ', end='')
            print('|')

            rowChars = processRow(row, rowIdx)
            for elem in rowChars:
                print('| {} '.format(elem), end='')
            print('|')

            for _ in range(boardLen):
                print('|____', end='')
            print('|')

        print('\nReadable')
        for rowIdx, row in enumerate(self.state.state):
            for elem in row:
                print('{} '.format(readableSigns[elem]), end='')
            print()

oth = Othello()
oth.fightAI(OthNode)
