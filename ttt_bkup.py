# play tic tac toe

import numpy as np
import random

class TTT:
    def __init__(self):
        self.board = np.zeros((3, 3))
        self.signs = {0: ' ', -1: 'X', 1: 'O'}
        self.x = True

    def isTerminal(self):
        for idx, row in enumerate(self.board):
            if np.abs(np.sum(row)) == 3:
                return row[0]
            col = self.board[:, idx]
            if np.abs(np.sum(col)) == 3:
                return col[0]
        if self.board[0][0] == self.board[1][1] == self.board[2][2] and self.board[1][1] != 0:
            return self.board[1][1]
        if self.board[2][0] == self.board[1][1] == self.board[0][2] and self.board[1][1] != 0:
            return self.board[1][1]
        if 0 not in self.board:
            return 0
        return None

    def printBoard(self):
        for idx, row in enumerate(self.board):
            print('   |   |   ')
            print(' {} | {} | {} '.format(self.signs[row[0]], self.signs[row[1]], self.signs[row[2]]))
            if idx != 2:
                print('___|___|___')

    def play(self, x, y, verbose=True):
        assert self.board[y][x] == 0

        if self.x:
            self.board[y][x] = -1
        else:
            self.board[y][x] = 1

        if verbose:
            self.printBoard()

        self.x = not self.x
        return self.isTerminal()

    def printTemp(self):
        print('---------------')
        print('   |   |   ')
        print(' 0 | 1 | 2 ')
        print('___|___|___')
        print('   |   |   ')
        print(' 3 | 4 | 5 ')
        print('___|___|___')
        print('   |   |   ')
        print(' 6 | 7 | 8 ')
        print('   |   |   ')
        print('---------------')

    def game(self, verbose=True):
        ended = None
        while ended is None:
            self.printTemp()

            if self.x:
                character = 'X'
            else:
                character = 'O'

            playerInp = int(input('({}) What position do you want? '.format(character)))
            y, x = playerInp // 3, playerInp % 3
            ended = self.play(x, y, verbose)
        if ended == -1:
            print('X wins')
        elif ended == 1:
            print('O wins')
        else:
            print('Tie')

    def simulate(self):
        pass

ttt = TTT()
ttt.game()
