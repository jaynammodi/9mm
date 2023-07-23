import random
from tkinter import *
import tkinter.font as font
from games import NMensMorris

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
GameSteps = ['Setup', 'Move', 'Remove']
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
        self.player1tokens = 9
        self.player2tokens = 9
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
        self.player1tokens = 9
        self.player2tokens = 9

        self.player1.poses = []
        self.player2.poses = []

        self.player1.numWin = 0
        self.player2.numWin = 0

        self.player1.picked = None
        self.player2.picked = None

        self.player1.step = GameSteps[0]
        self.player2.step = GameSteps[0]

        for row in self.cells:
            for x in row:
                x.button.config(state='normal', text="", bg="pink")
        
        self.enableEmptyCells()

        print("-----------------START-----------------")

    def quit(self):
        self.parent.destroy()

    def disable_game(self):
        """
        This function deactivates the game after a win, loss or draw or error.
        """
        for row in self.cells:
            for x in row:
                x.button.config(state='disable', text="")

    def disable_after_win(self, winner):
        """
        This function deactivates the game after a win, loss or draw or error.
        """
        for row in self.cells:
            for x in row:
                if x.button["text"] == winner:
                    x.button.config(state='disable', bg='yellow')
                elif x.button["text"] != "":
                    x.button.config(state='disable', bg='red')
                else:
                    x.button.config(state='disable', bg='black')

    def check_win(self):
        # if player 1 has 2 or less pieces, player 2 wins
        # if player 2 has 2 or less pieces, player 1 wins
        if self.player1tokens == 0 and self.player2tokens == 0:
            if(len(self.player1.poses) < 3):
                print("-----------------P2 WINS-----------------")
                # print("Player 2 wins!")
                self.disable_after_win("O")
                return True
            elif(len(self.player2.poses) < 3):
                print("-----------------P1 WINS-----------------")
                # print("Player 1 wins!")
                self.disable_after_win("X")
                return True
        return False

    def on_click(self, button):
        """ is used to step through the game. If Player1 is Human, then on_click is called when Human
        player clicks on an available spot. In case of AI vs AI playing, on_click is called as result
        of pressing 'next' button. """
        print("-----------------------------------------------")
        x, y = self.getCoordinates(button)

        if self.player1.step == GameSteps[0]:
            if self.player1tokens > 1:
                self.player1.poses.append([x, y])
                self.player1tokens -= 1
                button.config(text=self.to_move, state='disabled', disabledforeground="green")
                # print(" P1 > onClick: button.text=", button['text'], "pos: ", x, ", ", y)
                print(" P1 > Added token to pos: ", [x, y], " tokens left: ", self.player1tokens)
            elif self.player1tokens == 1:
                self.player1.poses.append([x, y])
                self.player1tokens -= 1
                self.player1.step = GameSteps[1]
                button.config(text=self.to_move, state='disabled', disabledforeground="green")
                # print(" P1 > onClick: button.text=", button['text'], "pos: ", x, ", ", y)
                print(" P1 > Added token to pos: ", [x, y], " tokens left: ", self.player1tokens)
                print("--------------BEGINNING MOVE PHASE-----------------")
                self.enablePlayerCells(self.player1.poses)
                self.disablePlayerCells(self.player2.poses)
                self.disableEmptyCells()

            check3_p1 = self.check3inRow(self.to_move, [x, y])
            # print(" P1 > setup check3inrow X , ", x, y ," : ", self.check3inRow("X", [x, y]))
            if check3_p1 == True:
                print(" P1 > 3inaRow Detected, Remove P2 Piece")
                self.player1.step = GameSteps[2]
                self.enablePlayerCells(self.player2.poses)
                self.disablePlayerCells(self.player1.poses)
                self.disableEmptyCells()
                return
            
        elif self.player1.step == GameSteps[1]:
            # add the logic for move here:
            if [x, y] in self.player1.poses:
                self.player1.picked = [x, y]
                print(" P1 > item at cell index ", self.player1.picked , " picked")
                self.disablePlayerCells(self.player1.poses)
                self.disablePlayerCells(self.player2.poses)
                self.enableEmptyCells()
                return
                
            elif self.player1.picked is not None:
                start = self.player1.picked
                print(" P1 > move item from loc [", start[0], ", ",start[1], "] to location [", x, ",", y, "]")
                
                if self.move(start, [x,y]) == True:
                    self.player1.poses.remove(start)
                    self.player1.poses.append([x,y])
                else:
                    print(" P1 > move failed")
                    return
                self.player1.picked = None

                self.enablePlayerCells(self.player1.poses)
                self.disablePlayerCells(self.player2.poses)
                self.disableEmptyCells()

                check3_p1 = self.check3inRow(self.to_move, [x, y])
                # print(" P1 > Move check3inrow X , ", x, y ," : ", self.check3inRow("X", [x, y]))
                if check3_p1 == True:
                    print(" P1 > 3inaRow Detected, Remove P2 Piece")
                    # print("--------------3inaRow Detected, Remove P2 Piece-----------------")
                    self.player1.step = GameSteps[2]
                    self.enablePlayerCells(self.player2.poses)
                    self.disablePlayerCells(self.player1.poses)
                    self.disableEmptyCells()
                    return

        elif self.player1.step == GameSteps[2]:
            # add the logic to remove opponent piece here:
            if [x, y] in self.player2.poses:
                # check if the piece is in a 3-in-a-row, if it is it cannot be removed
                if self.check3inRow("O", [x, y]) == True and len(self.player2.poses) > 3:
                    print(" P1 > Cannot remove piece in 3-in-a-row")
                    return
                self.player2.poses.remove([x, y])
                button.config(text="", state='normal')
                print(" P1 > item at cell index ", [x, y], " removed")
                if self.check_win():
                    return
                self.disablePlayerCells(self.player2.poses)
                self.disablePlayerCells(self.player1.poses)
                self.disableEmptyCells()
                if self.player1tokens == 0:
                    self.player1.step = GameSteps[1]
                    self.enablePlayerCells(self.player1.poses)
                else:
                    self.player1.step = GameSteps[0]
                    self.enableEmptyCells()

        if self.to_move == "X":
            self.to_move = "O"
        else:
            self.to_move = "X"

        a, b = self.randomMove()
        pos = self.cells[a][b].pos
        if a != -1 and b != -1:
            if self.player2.step == GameSteps[0]:
                if self.player2tokens > 1:
                    self.player2.poses.append(pos)
                    self.player2tokens -= 1
                    self.cells[a][b].button.config(text=self.to_move, state='disabled', disabledforeground="blue")
                    # print(" P2 > onClick: Opponent button.text=", self.cells[a][b].button['text'], "pos: ", pos[0], ", ", pos[1])
                    print(" P2 > Added token to pos: ", [a, b], " tokens left: ", self.player2tokens)
                    self.cells[a][b].button.config(text=self.to_move, state='disabled', disabledforeground="blue")
                    # self.to_move = "X"
                elif self.player2tokens == 1:
                    # self.player2.poses.append([a, b])
                    self.player2.poses.append(pos)
                    self.player2tokens -= 1
                    self.player2.step = GameSteps[1]
                    self.cells[a][b].button.config(text=self.to_move, state='disabled', disabledforeground="blue")
                    # print(" P2 > onClick: Opponent button.text=", self.cells[a][b].button['text'], "pos: ", pos[0], ", ", pos[1])
                    print(" P2 > Added token to pos: ", [a, b], " tokens left: ", self.player2tokens)
                    print("--------------BEGINNING MOVE PHASE-----------------")
                    self.cells[a][b].button.config(text=self.to_move, state='disabled', disabledforeground="blue")
                    # self.to_move = "X"
                    # self.enablePlayerCells(self.player2.poses)

                check3_p2 = self.check3inRow(self.to_move, pos)
                # print(" P2 > setup check3inrow O , ", pos ," : ", self.check3inRow("O", pos))

                if check3_p2 == True:
                    # print("--------------3inaRow Detected, Removing P1 Piece-----------------")
                    print(" P2 > 3inaRow Detected, Removing P1 Piece")
                    # add logic for randomly choosing and removing one of opponents pieces
                    rem = self.chooseRandomToRemove(self.player1.poses)
                    print(" P2 > remove opponent piece at ", rem)
                    self.player1.poses.remove(rem)
                    self.getButton(rem).config(text="", state='normal')
                    # self.cells[rem[0]][rem[1]].button.config(text="", state='normal')
                    print(" P2 > item at cell index ", rem, " removed")
                    if self.check_win():
                        return
                    # self.disablePlayerCells(self.player1.poses)
                    if self.player2tokens == 0:
                        self.player2.step = GameSteps[1]
                        # self.enablePlayerCells(self.player2.poses)
                    else:
                        self.player2.step = GameSteps[0]
                    
                
            elif self.player2.step == GameSteps[1]:
                a, b, x, y = self.makeRandomMove()
                # implement logic for AI move here:
                if [a, b] in self.player2.poses:
                    self.player2.picked = [a, b]
                    print(" P2 > item at cell index ", self.player2.picked, " picked")
                    start = self.player2.picked
                    print(" P2 > move item from loc [", start[0], ", ", start[1], "] to location [", x, ",", y, "]")
                    if self.move(start, [x, y]) == True:
                        self.player2.poses.remove(start)
                        self.player2.poses.append([x, y])
                        self.getButton([x,y]).config(text=self.to_move, state='disabled', disabledforeground="blue")
                        self.getButton([a,b]).config(text="", state='normal')
                    self.player2.picked = None
                
                check3_p2 = self.check3inRow(self.to_move, [x,y])
                # print(" P2 > Move check3inrow O , ", pos ," : ", self.check3inRow("O", [x,y]))

                if check3_p2 == True:
                    # print("--------------3inaRow Detected, Removing P1 Piece-----------------")
                    print(" P2 > 3inaRow Detected, Removing P1 Piece")
                    # add logic for randomly choosing and removing one of opponents pieces
                    rem = self.chooseRandomToRemove(self.player1.poses)
                    print(" P2 > remove opponent piece at ", rem)
                    self.player1.poses.remove(rem)
                    self.getButton(rem).config(text="", state='normal')
                    # self.cells[rem[0]][rem[1]].button.config(text="", state='normal')
                    print(" P2 > item at cell index ", rem, " removed")
                    if self.check_win():
                        return
                    # self.disablePlayerCells(self.player1.poses)
                    if self.player2tokens == 0:
                        self.player2.step = GameSteps[1]
                        # self.enablePlayerCells(self.player2.poses)
                    else:
                        self.player2.step = GameSteps[0]
                    

            if self.to_move == "X":
                self.to_move = "O"
            else:
                self.to_move = "X"
        else:
            print("!!Error in finding available free spot. Disabling the game!\n")
            self.disable_game()

        if self.check_win():
            return
        
    def getButton(self, pos):
        """Get the button at the given position"""
        for i in range(7):
            row = self.cells[i]
            for j in range(len(row)):
                if self.cells[i][j].pos == pos:
                    return self.cells[i][j].button

    def chooseRandomToRemove(self, list):
        """Choose a random element from the list"""
        sol = random.choice(list)
        while self.check3inRow("X", sol) == True and len(list) > 3:
            sol = random.choice(list)
        return sol

    def check3inRow(self, player, cur_move):
        """Check if the player has 3 in a row"""

        plausible_matches = [
            # diagonals
            [[0, 0], [1, 1], [2, 2]],
            [[0, 6], [1, 5], [2, 4]],
            [[6, 0], [5, 1], [4, 2]],
            [[6, 6], [5, 5], [4, 4]],
            [[3, 1], [4, 2], [5, 3]],
            [[5, 3], [4, 4], [3, 5]],
            [[3, 1], [2, 2], [1, 3]],
            [[1, 3], [2, 4], [3, 5]],

            # verticals
            [[2, 2], [3, 2], [4, 2]],
            [[2, 4], [3, 4], [4, 4]],
            [[0, 3], [1, 3], [2, 3]],
            [[4, 3], [5, 3], [6, 3]],

            # horizontals
            [[2, 2], [2, 3], [2, 4]],
            [[4, 2], [4, 3], [4, 4]],
            [[3, 0], [3, 1], [3, 2]],
            [[3, 4], [3, 5], [3, 6]],
        ]

        for match in plausible_matches:
            if cur_move in match:
                # print("possible rows:" , match)
                if player == "X":
                    # print([locs in self.player1.poses for locs in match])
                    if all(locs in self.player1.poses for locs in match):
                        self.player1.numWin += 1
                        return True
                elif player == "O":
                    if all(locs in self.player2.poses for locs in match):
                        self.player2.numWin += 1
                        return True
        return False

    def removePlayer1Pose(self, pose):
        """remove the pose from the player's poses"""
        self.player1.poses.remove(pose)
        self.cells[pose[0]][pose[1]].button.config(text="", state='normal')

    def removePlayer2Pose(self, pose):
        """remove the pose from the player's poses"""
        self.player2.poses.remove(pose)
        self.cells[pose[0]][pose[1]].button.config(text="", state='normal')

    def makeRandomMove(self):
        """make a random move for the AI player"""
        a = -1
        b = -1
        available_moves = []
        while available_moves == []:
            a, b = random.choice(self.player2.poses)
            available_moves = self.getAvailableMovesForPos(a, b)
        x, y = random.choice(available_moves)
        return a, b, x, y
        
    def getAvailableMoves(self, pose):
        """get available moves for the pose"""
        return self.getAvailableMovesForPos(pose[0], pose[1])
    
    def getAvailableMovesForPos(self, x, y):
        """get available moves for the position x, y"""
        moves = []
        vacant_cells = []
        for row in self.cells:
            for cell in row:
                if cell.button["text"] == "":
                    vacant_cells.append(cell.pos)
        for i in range(-1, 2):
            for j in range(-1, 2):
                x1 = x + i
                y1 = y + j
                if [x1, y1] in vacant_cells:
                    moves.append([x1, y1])
        return moves

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

    def disablePlayerCells(self, poses):
        """go through all the cells occupied by positions in pos array and disable their buttons for clicking"""
        for pos in poses:
            for row in self.cells:
                for cell in row:
                    if cell.pos == pos:
                        if cell.button["text"] == "X":
                            cell.button.config(state='disabled', disabledforeground='green')
                        elif cell.button["text"] == "O":
                            cell.button.config(state='disabled', disabledforeground='blue')

    def enableEmptyCells(self):
        """enable all the empty cells for clicking"""
        for row in self.cells:
            for cell in row:
                if cell.button["text"] == "":
                    cell.button.config(state='normal')

    def disableEmptyCells(self):
        """disable all the empty cells for clicking"""
        for row in self.cells:
            for cell in row:
                if cell.button["text"] == "":
                    cell.button.config(state='disabled')

    def move(self, start, end):
        """try to move a player from start to end position"""
        legal_moves = self.getAvailableMoves(start)
        if end not in legal_moves:
            print("move: Error: end position is not a legal move")
            return False
        
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
