
import copy
import itertools
import random
from collections import namedtuple

import numpy as np

from utils import vector_add

GameState = namedtuple('GameState', 'to_move, utility, board, moves')
StochasticGameState = namedtuple('StochasticGameState', 'to_move, utility, board, moves, chance')


GameState = namedtuple('GameState', 'to_move, utility, board, moves')

def gen_state(to_move='X', x_positions=[], o_positions=[], h=3, v=3):
    """Given whose turn it is to move, the positions of X's on the board, the
    positions of O's on the board, and, (optionally) number of rows, columns
    and how many consecutive X's or O's required to win, return the corresponding
    game state"""

    moves = set([(x, y) for x in range(1, h + 1) for y in range(1, v + 1)]) - set(x_positions) - set(o_positions)
    moves = list(moves)
    board = {}
    for pos in x_positions:
        board[pos] = 'X'
    for pos in o_positions:
        board[pos] = 'O'
    return GameState(to_move=to_move, utility=0, board=board, moves=moves)


# ______________________________________________________________________________
# MinMax Search


def minmax_decision(state, game):
    """Given a state in a game, calculate the best move by searching
    forward all the way to the terminal states. [Figure 5.3]"""

    player = game.to_move(state)

    def max_value(state):
        if game.terminal_test(state):
            return game.utility(state, player)
        v = -np.inf
        for a in game.actions(state):
            v = max(v, min_value(game.result(state, a)))
        return v

    def min_value(state):
        if game.terminal_test(state):
            return game.utility(state, player)
        v = np.inf
        for a in game.actions(state):
            v = min(v, max_value(game.result(state, a)))
        return v

    # Body of minmax_decision:
    return max(game.actions(state), key=lambda a: min_value(game.result(state, a)))


# ______________________________________________________________________________


def expect_minmax(state, game):
    """
    [Figure 5.11]
    Return the best move for a player after dice are thrown. The game tree
	includes chance nodes along with min and max nodes.
	"""
    player = game.to_move(state)

    def max_value(state):
        v = -np.inf
        for a in game.actions(state):
            v = max(v, chance_node(state, a))
        return v

    def min_value(state):
        v = np.inf
        for a in game.actions(state):
            v = min(v, chance_node(state, a))
        return v

    def chance_node(state, action):
        res_state = game.result(state, action)
        if game.terminal_test(res_state):
            return game.utility(res_state, player)
        sum_chances = 0
        num_chances = len(game.chances(res_state))
        for chance in game.chances(res_state):
            res_state = game.outcome(res_state, chance)
            util = 0
            if res_state.to_move == player:
                util = max_value(res_state)
            else:
                util = min_value(res_state)
            sum_chances += util * game.probability(chance)
        return sum_chances / num_chances

    # Body of expect_minmax:
    return max(game.actions(state), key=lambda a: chance_node(state, a), default=None)


def alpha_beta_search(state, game):
    """Search game to determine best action; use alpha-beta pruning.
    As in [Figure 5.7], this version searches all the way to the leaves."""

    player = game.to_move(state)

    # Functions used by alpha_beta
    def max_value(state, alpha, beta):
        if game.terminal_test(state):
            return game.utility(state, player)
        v = -np.inf
        for a in game.actions(state):
            v = max(v, min_value(game.result(state, a), alpha, beta))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(state, alpha, beta):
        if game.terminal_test(state):
            return game.utility(state, player)
        v = np.inf
        for a in game.actions(state):
            v = min(v, max_value(game.result(state, a), alpha, beta))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    # Body of alpha_beta_search:
    best_score = -np.inf
    beta = np.inf
    best_action = None
    for a in game.actions(state):
        v = min_value(game.result(state, a), best_score, beta)
        if v > best_score:
            best_score = v
            best_action = a
    return best_action


def alpha_beta_cutoff_search(state, game, d=4, cutoff_test=None, eval_fn=None):
    """Search game to determine best action; use alpha-beta pruning.
    This version cuts off search and uses an evaluation function."""

    player = game.to_move(state)

    # Functions used by alpha_beta
    def max_value(state, alpha, beta, depth):
        if cutoff_test(state, depth):
            return eval_fn(state)
        v = -np.inf
        for a in game.actions(state):
            v = max(v, min_value(game.result(state, a), alpha, beta, depth + 1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(state, alpha, beta, depth):
        if cutoff_test(state, depth):
            return eval_fn(state)
        v = np.inf
        for a in game.actions(state):
            v = min(v, max_value(game.result(state, a), alpha, beta, depth + 1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    # Body of alpha_beta_cutoff_search starts here:
    # The default test cuts off at depth d or at a terminal state
    cutoff_test = (cutoff_test or (lambda state, depth: depth > d or game.terminal_test(state)))
    eval_fn = eval_fn or (lambda state: game.utility(state, player))
    best_score = -np.inf
    beta = np.inf
    best_action = None
    for a in game.actions(state):
        v = min_value(game.result(state, a), best_score, beta, 1)
        if v > best_score:
            best_score = v
            best_action = a
    return best_action


# ______________________________________________________________________________
# Players for Games

def query_player(game, state):
    """Make a move by querying standard input."""
    print("current state:")
    game.display(state)
    print("available moves: {}".format(game.actions(state)))
    print("")
    move = None
    if game.actions(state):
        move_string = input('Your move? ')
        try:
            move = eval(move_string)
        except NameError:
            move = move_string
    else:
        print('no legal moves: passing turn to next player')
    return move


def random_player(game, state):
    """A player that chooses a legal move at random."""
    return random.choice(game.actions(state)) if game.actions(state) else None


def alpha_beta_player(game, state):
    return alpha_beta_search(state, game)


def minmax_player(game,state):
    return minmax_decision(state,game)


def expect_minmax_player(game, state):
    return expect_minmax(state, game)

class Game:
    """A game is similar to a problem, but it has a utility for each
    state and a terminal test instead of a path cost and a goal
    test. To create a game, subclass this class and implement actions,
    result, utility, and terminal_test. You may override display and
    successors or you can inherit their default methods. You will also
    need to set the .initial attribute to the initial state; this can
    be done in the constructor."""

    def actions(self, state):
        """Return a list of the allowable moves at this point."""
        raise NotImplementedError

    def result(self, state, move):
        """Return the state that results from making a move from a state."""
        raise NotImplementedError

    def utility(self, state, player):
        """Return the value of this final state to player."""
        raise NotImplementedError

    def terminal_test(self, state):
        """Return True if this is a final state for the game."""
        return not self.actions(state)

    def to_move(self, state):
        """Return the player whose move it is in this state."""
        return state.to_move

    def display(self, state):
        """Print or otherwise display the state."""
        print(state)

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    def play_game(self, *players):
        """Play an n-person, move-alternating game."""
        state = self.initial
        while True:
            for player in players:
                move = player(self, state)
                state = self.result(state, move)
                if self.terminal_test(state):
                    self.display(state)
                    return self.utility(state, self.to_move(self.initial))


class NMensMorris(Game):
    '''
           A simple Gameboard for 9MensMorris game class. This class contains all game specifics logic like
           what next move to take, if a point (completing a row or diagonal or column) been achieved, if
           game is terminated, and so on. For deciding on next move, there are 3 phases to the game:
            •	Placing pieces on vacant points (9 turns each)
            •	Moving placed pieces to adjacent points.
            •	Moving pieces to any vacant point (when the player has been reduced to 3 men)

            This class governs all the logic of the game. This means it has to check validity of each player's
            move, as well as deciding on next move for the AI player. This class receives the game state,
            in form of the list of rows of cells on the board.

        '''
    def __init__(self, h=3, v=3, k=3):
        self.h = h
        self.v = v
        self.k = k
        board = []  # an array of 7 rows, each row an array of element from set {'X', 'O', '-'}.
                    #. 'X' means occupied by Human player, 'O' is occupied by AI, '-' means still vacant
        self.initial = GameState(to_move='X', utility=0, board={}, moves={})

    def actions(self, state):
        """Legal moves are any square not yet taken."""
        return state.moves

    def result(self, state, move):
        if move not in state.moves:
            return state  # Illegal move has no effect
        board = state.game.copy()
        board[move] = state.to_move
        moves = list(state.moves)
        moves.remove(move)
        return GameState(to_move=('O' if state.to_move == 'X' else 'X'),
                         utility=self.compute_utility(board, move, state.to_move),
                         board=board, moves=moves)

    def utility(self, state, player):
        """Return the value to player; 1 for win, -1 for loss, 0 otherwise."""
        return state.utility if player == 'X' else -state.utility

    def is_legal_move(self, board, start, end, player):
        """ can be used to check if a move from start to end positions by player. This function can
        be called for example by get_all_moves() for checking validity of on-board piece moves
        """
        pass

    def get_all_moves(self, board, player):
        """All possible moves for a player. Depending of the state of the game, it can
        include all positions to put a new piece, or all position to move the current pieces.
        The design and format is for students' to do"""
        pass

    def terminal_test(self, state):
        """A state is terminal if it is won or there are no empty squares."""
        return state.utility != 0 or len(state.moves) == 0

    def display(self, state):
        board = state.game
        for x in range(1, self.h + 1):
            for y in range(1, self.v + 1):
                print(board.get((x, y), '.'), end=' ')
            print()

    def compute_utility(self, board, move, player):
        """If 'X' wins with this move, return 1; if 'O' wins return -1; else return 0."""
        if (self.k_in_row(board, move, player, (0, 1)) or
                self.k_in_row(board, move, player, (1, 0)) or
                self.k_in_row(board, move, player, (1, -1)) or
                self.k_in_row(board, move, player, (1, 1))):
            return +1 if player == 'X' else -1
        else:
            return 0

    def k_in_row(self, board, move, player, delta_x_y):
        """Return true if there is a line through move on board for player."""
        (delta_x, delta_y) = delta_x_y
        x, y = move
        n = 0  # n is number of moves in row
        while board.get((x, y)) == player:
            n += 1
            x, y = x + delta_x, y + delta_y
        x, y = move
        while board.get((x, y)) == player:
            n += 1
            x, y = x - delta_x, y - delta_y
        n -= 1  # Because we counted move itself twice
        return n >= self.k

import random
from tkinter import *
import tkinter.font as font
# from games import NMensMorris

"""
Playertype Options are Human: # means this is human player. Then the player has to manually click on spots on gameboard to make a move
Random: # For AI player. Chooses randomly among all possible move options
MinMax: # For AI player. Uses MinMax adversarial algorithm all the way to the leaf nodes 
AlphaBeta(MinMax with Alpha-Beta Pruning): # For AI player. Uses AlphaBeta algorithm all the way to the leaf
AlphaBetaCutoff (AlphaBeta with cutoff depth): # For AI player. Similar to AlphaBeta case, except now the computation is cutoff at a depth d and an evaluation function is used at that level for Utility value
ExpectimaxCutoff: Use chance nodes instead of the min nodes. This means at min level, use average of all successors' utility value. Similar to abov case, computation is cutoff at depth d
"""
PlayerType = ["Human", "Random", "MinMax", "AlphaBeta", "AlphaBetaCutoff", "ExpectimaxCutoff"]
class Cell:
    pos = [0, 0]
    button = None
    def __init__(self, pos, btn):
        self.pos = pos
        self.button = btn

"""# game has 2 steps for each player: setting up step in which player is setting up his 9 pieces,
and next step is 'Move' step where she is moving her pieces around the board. """
GameSteps = ['Setup', 'Move']
class NMMPlayer:
    def __init__(self, id, type):
        self.id = 'X'
        self.type = type
        self.step = GameSteps[0]
        self.utility = 0
        self.poses = []  # array of position pair (row, col) for all the pieces of this player on board.
                        # max size of pos is 9
        self.numWin = 0    # number of 3-lineup wins during this game for this player so far
        self.picked = None  # picked position for the moving step
class BoardGui(Frame):
    cells = []  # all the cells of the board
    to_move = "X"  # It can have 2 values: X for human player  or O for AI player
    dims = 7  # game board dimension : 7 x 7

    def __init__(self, parent, board):

        self.depth = -1  # -1 means search up to leaf level. So no restriction
        self.player1 = NMMPlayer(0, PlayerType[0])
        self.player2 = NMMPlayer(1, PlayerType[1])
        self.game = board
        self.parent = parent

        # setup the game board:
        for i in range(self.dims):
            parent.columnconfigure(i, weight=1, minsize=75)
            parent.rowconfigure(i, weight=1, minsize=50)
            cellsInFrame = []
            for j in range(0, self.dims):
                frame = Frame( master=parent, relief=RAISED, borderwidth=1)
                frame.grid(row=i, column=j, padx=5, pady=5)
                if(     (i%6==0 and j%3 == 0) or
                        (i%4==1 and j%2==1 ) or
                        ((i==2 or i==4) and (j==2 or j==3 or j==4)) or
                        (i==3 and j!=3)      ):
                    button = Button(master=frame, width=3, text="", bg="pink")
                    button['font'] = font.Font(family='Helvetica')
                    button.config(command=lambda btn=button: self.on_click(btn))
                    button.pack(padx=5, pady=5)
                    cellsInFrame.append(Cell([i, j], button))
                elif(i==3 and j==3):
                    frame.config(height= 30, width=30, bg='black')
                else:
                    frame.config(height=3, bg='black', width=30)

            self.cells.append(cellsInFrame)

        # setup the UI panel:
        parent.rowconfigure(self.dims, weight=1, minsize=75)

        newButton = Button(parent, text="New", fg="white", bg="blue", command=self.reset)
        newButton.grid(row=self.dims, column=0, padx=5, pady=5)

        quitButton = Button(parent, text="Quit", fg="white", bg="black", command=self.quit)
        quitButton.grid(row=self.dims, column=1, padx=5, pady=5)

        """Player1 can be either Human or AI player"""
        choiceStr = StringVar(parent)
        choiceStr.set(PlayerType[0])
        menu = OptionMenu(parent, choiceStr, *PlayerType, command=self.set_player1)
        menu.grid(row=self.dims, column=2, padx=1, pady=5)

        """Player2 can be only AI player"""
        choiceStr = StringVar(parent)
        choiceStr.set(PlayerType[1])
        menu = OptionMenu(parent, choiceStr, *PlayerType[1:], command=self.set_player2)
        menu.grid(row=self.dims, column=3, padx=1, pady=5)

        """next button is used to step through the game when 2 AI players are playing against each other.
         Each clicking on next plays one sequence of Player1-Player2"""
        nextButton = Button(master=parent, text="next", borderwidth=1, border=1)
        nextButton.grid(row=self.dims, column=4, padx=1, pady=5)

        depthLabel = Label(master=parent, text="Depth:", width=10)
        depthLabel.grid(row=self.dims, column=5, padx=1, pady=5)
        depthStr = StringVar()
        depthStr.set(str(self.depth))
        depthEntry = Entry(parent, width =7, textvariable=depthStr)
        depthEntry.grid(row=self.dims, column=6, padx=1, pady=5)


    def set_player1(self, choice):
        """ Set the level of first player. If chosen Human, it is human player.
        """
        self.player1.type = choice
        print("set_player1: level set to ", self.player1.type)

    def set_player2(self, choice):
        """ Set the level of second player. Same as above.
        """
        self.player2.type = choice
        print("set_player2: level set to ", self.player2.type)

    def set_depth(self, choice):
        """Sets the depth to be used for cut-off searches for corresponding search: alpha_beta_cutoff
        Note: This is used for any player with type which use depth value
        """
        self.depth = choice
        print("set_depth: depth set to ", choice)

    def getCoordinates(self, btn):
        try:
            for i in range(self.dims):
                row = self.cells[i]
                for j in range(len(row)):
                    if row[j].button == btn:
                        return row[j].pos
        except IndexError:
            print("ERROR! getCoordinate(): could not find the button's indices\n")
            return

    def printBoard(self):
        try:
            for i in range(self.dims):
                for j in range(self.cells[i]):
                    cell = self.cells[i][j]
                    print("Cell: ",i, ", ",j, ", text:", cell.button["text"])
                print("\n")
        except IndexError:
            print("printboard: index error ")


    def reset(self):
        """reset the game's board"""
        for row in self.cells:
            for x in row:
                x.button.config(state='normal', text="")

    def quit(self):
        self.parent.destroy()

    def disable_game(self):
        """
        This function deactivates the game after a win, loss or draw or error.
        """
        for row in self.cells:
            for x in row:
                x.button.config(state='disable', text="")

    def on_click(self, button):
        """ is used to step through the game. If Player1 is Human, then on_click is called when Human
        player clicks on an available spot. In case of AI vs AI playing, on_click is called as result
        of pressing 'next' button. """
        x, y = self.getCoordinates(button)

        if self.player1.step == GameSteps[0]:
            if len(self.player1.poses) < 8:
                self.player1.poses.append([x, y])
                button.config(text=self.to_move, state='disabled', disabledforeground="green")
                print("onClick: button.text=", button['text'], "pos: ", x, ", ", y)
            elif len(self.player1.poses) == 8:
                self.player1.poses.append([x, y])
                self.player1.step = GameSteps[1]
                button.config(text=self.to_move, state='disabled', disabledforeground="green")
                print("onClick: button.text=", button['text'], "pos: ", x, ", ", y)
                self.enablePlayerCells(self.player1.poses)
        else:
            # add the logic for move here:
            if [x, y] in self.player1.poses:
                self.player1.picked = [x, y]
                print("item at cell index ", self.player1.picked , " picked")
            elif self.player1.picked is not None:
                start = self.player1.picked
                print("move item from loc [", start[0], ", ",start[1], "] to location [", x, ",", y, "]")
                if self.move(start, [x,y]) == True:
                    self.player1.poses.remove(start)
                    self.player1.poses.append([x,y])
                self.player1.picked = None


        if self.to_move == "X":
            self.to_move = "O"
        else:
            self.to_move = "X"

        # select a move for AI. For now we choose a random available position.
        # Note: This code is temporary,just to have a random player for demo. THe proper place for the
        #       following functionality in in NMenMorris class, to be done by students.
        a, b = self.randomMove()
        if a != -1 and b != -1:
            if self.player2.step == GameSteps[0]:
                if len(self.player2.poses) < 9:
                    self.player2.poses.append([a, b])
                    self.cells[a][b].button.config(text=self.to_move, state='disabled', disabledforeground="blue")
                    print("onClick: Opponent button.text=", self.cells[a][b].button['text'], "pos: ", a, ", ", b)
                    self.cells[a][b].button.config(text=self.to_move, state='disabled', disabledforeground="blue")
                    self.to_move = "X"
        else:
            print("!!Error in finding available free spot. Disabling the game!\n")
            self.disable_game()


    def randomMove(self):
        """Randomly pick a free position on the board
        Note: This is temporary, and students will move this code to NMensMorris class as part of the assignment tasks"""
        upperCap = 50 # after some number (here 50) of trial if we can't find available spot, return -1
        while(upperCap > 0):
            a = random.choice(range(7))
            b = random.randrange(len(self.cells[a]))
            upperCap -= 1
            if(self.cells[a][b].button["text"] == ""):
                return a, b

        print("Error! randomMove(): no available pos found in the board. Something is wrong!")
        return -1, -1

    def enablePlayerCells(self, poses):
        """go through all the cells occupied by positions in pos array and enable their buttons for clicking"""
        for pos in poses:
            for row in self.cells:
                for cell in row:
                    if cell.pos == pos:
                        cell.button.config(state='normal')

    def move(self, start, end):
        """try to move a player from start to end position"""
        x, y = start
        a, b = end
        for sCell in self.cells[x]:
            if sCell.pos == start:
                assert sCell.button["text"]!="", "move: Error: start cell cannot be empty"
                for eCell in self.cells[a]:
                    if eCell.pos == end:
                        if eCell.button["text"] == "":
                            eCell.button["text"] = sCell.button["text"]
                            sCell.button["text"] = ""
                            return True
                        else:
                            print("move: end cell is not empty! Ignoring move")


        return False


def initialize(nmm):
    root = Tk()
    root.title("9 MensMorris Game")

    gui = BoardGui(root, nmm)

    root.resizable(1,1)
    root.mainloop()

if __name__ == "__main__":
    game = NMensMorris()
    initialize(game)
