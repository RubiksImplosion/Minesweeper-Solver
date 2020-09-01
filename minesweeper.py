import tkinter as tk
from tkinter import font
import random
import math
import time

class Minesweeper(tk.Frame):
    def __init__(self,master=None):
        super().__init__(master)
        self.master = master
        self.job = None
        self.solving = False
        #self.board = Board(master=self.master,x=20,y=20,m=.05)
        self.board = Board(master=self.master,x=30,y=15,m=0.15)
        self.revealedMines = 0
        self.setup()

    def setup(self):
        self.cancelActiveJob()
        self.board.statusLabel.destroy()
        self.board = Board(master=self.master,x=self.board.x,y=self.board.y,m=self.board.m)
        self.display()
        self.revealedMines = 0
        self.solving = False
        
    def display(self):
        counter = 0
        for r in range(self.board.y):
            for c in range(self.board.x):
                self.board.board[counter][0].grid(row=r+1,column=c)
                counter += 1

    def processClick(self,pos,value):
        if value > 0:
            self.board.board[pos][0].text.set(str(value))
            self.board.activeTiles -= 1
        else:
            self.board.spread(pos)
            self.board.activeTiles -= 1
        self.checkForCompletion()

    def clickMine(self):
        self.board.mineClicked = True
        for i in range(len(self.board.board)):
            self.board.board[i][0].flagged = False
            self.board.board[i][0].reveal()
        self.checkForCompletion()
        
    def checkForCompletion(self):
        if self.board.mineClicked:
            self.board.statusText.set("You Lose")
            #print("-------------------LOSE--------------------")
            self.board.statusLabel.configure(fg="red")
        elif self.board.activeTiles == 0:
            self.board.statusText.set("You Win")
            self.board.statusLabel.configure(fg="green")

    def startSolve(self):
        if not self.solving:
            self.solving = True
            self.solve()

    def solve(self):
        if self.board.activeTiles != 0:
            x = self.board.x
            y = self.board.y
            #Deals with the case that none of the tiles are revealed
            if self.board.activeTiles == (x*y)-self.board.mineCount:
                self.findStarterTile(x,y)

            #Deals with basic tile checks and logic for if advanced checks should be preformed
            update = False
            knownTiles = self.genKnownTiles(x,y)
            for tile in knownTiles:
                if self.basicTileCheck(tile,x,y):
                    update = True
            
            #Deals with advanced tile checks
            if not update:
                totalMines = self.board.mineCount
                #print("{} mines left".format(totalMines-self.revealedMines))
                #print("knownTiles:   {}".format(knownTiles))
                for tile in knownTiles:
                    self.advancedTileCheck(tile,x,y)

                
            #print("knownTiles:   {}".format(knownTiles))
            self.job = self.after(100,lambda:self.solve())

    def findStarterTile(self,x,y):
        counter = 0
        foundStarterTile = False
        while not self.board.mineClicked and not foundStarterTile:
            if not self.board.board[counter][0].clicked:
                self.board.board[counter][0].reveal()
                if self.board.board[counter][0].value == 0:
                    foundStarterTile = True
                counter += 1
            else:
                counter += 1

    def genKnownTiles(self,x,y):
        knownTiles = []
        for i in range(len(self.board.board)):
            if not self.board.board[i][0].clicked and not self.board.board[i][0].flagged:
                rightEdge = False
                leftEdge = False
                topEdge = False
                bottomEdge = False

                if (i+1) <= x:
                    topEdge = True
                if (i+1) % x == 0:
                    rightEdge = True
                if i % x == 0:
                    leftEdge = True
                if (i+1) > (y-1)*x:
                    bottomEdge = True
                
                if not topEdge:
                    if self.board.board[i-x][0].clicked:
                        knownTiles.append(i-x)
                if not rightEdge:
                    if self.board.board[i+1][0].clicked:
                        knownTiles.append(i+1)
                if not leftEdge:
                    if self.board.board[i-1][0].clicked:
                        knownTiles.append(i-1)
                if not bottomEdge:
                    if self.board.board[i+x][0].clicked:
                        knownTiles.append(i+x)
                if not topEdge and not rightEdge:
                    if self.board.board[i-(x-1)][0].clicked:
                        knownTiles.append(i-(x-1))
                if not topEdge and not leftEdge:
                    if self.board.board[i-(x+1)][0].clicked:
                        knownTiles.append(i-(x+1))
                if not bottomEdge and not rightEdge:
                    if self.board.board[i+(x+1)][0].clicked:
                        knownTiles.append(i+(x+1))
                if not bottomEdge and not leftEdge:
                    if self.board.board[i+(x-1)][0].clicked:
                        knownTiles.append(i+(x-1))
        return sorted(set(knownTiles))

    def basicTileCheck(self,tile,x,y):
        update = False
        tileValue = self.board.board[tile][0].value
        unknownTiles = self.getUnknownTilesAroundTile(tile,x,y)
        flaggedTiles = self.getFlaggedTilesAroundTile(tile,x,y)
        if tileValue - len(flaggedTiles) == 0:
            for candidate in unknownTiles:
                self.board.board[candidate][0].reveal()
                #print("Revealing tile {} with initial tile of {} with a value of {}".format(candidate,tile,tileValue))
                #print("- flaggedTiles set to {}".format(flaggedTiles))
                #print("- unknownTiles set to {}".format(unknownTiles))
                unknownTiles.remove(candidate)
                update = True
                #print("- removed tile {}; new unknownTiles value of {}".format(candidate,unknownTiles))
        if tileValue - len(flaggedTiles) == len(unknownTiles):
            for candidate in unknownTiles:
                self.board.board[candidate][0].flag()
                self.revealedMines += 1
                update = True
                #print("Flagging tile {} with initial tile of {} with a value of {}".format(candidate,tile,tileValue))
                #print("- flaggedTiles set to {}".format(flaggedTiles))
                #print("- unknownTiles set to {}".format(unknownTiles))
        return update
    
    def getUnknownTilesAroundTile(self,i,x,y):
        candidates = []
        rightEdge = False
        leftEdge = False
        topEdge = False
        bottomEdge = False

        if (i+1) <= x:
            topEdge = True
        if (i+1) % x == 0:
            rightEdge = True
        if i % x == 0:
            leftEdge = True
        if (i+1) > (y-1)*x:
            bottomEdge = True
        
        if not topEdge:
            if not self.board.board[i-x][0].clicked and not self.board.board[i-x][0].flagged:
                candidates.append(i-x)
        if not rightEdge:
            if not self.board.board[i+1][0].clicked and not self.board.board[i+1][0].flagged:
                candidates.append(i+1)
        if not leftEdge:
            if not self.board.board[i-1][0].clicked and not self.board.board[i-1][0].flagged:
                candidates.append(i-1)
        if not bottomEdge:
            if not self.board.board[i+x][0].clicked and not self.board.board[i+x][0].flagged:
                candidates.append(i+x)
        if not topEdge and not rightEdge:
            if not self.board.board[i-(x-1)][0].clicked and not self.board.board[i-(x-1)][0].flagged:
                candidates.append(i-(x-1))
        if not topEdge and not leftEdge:
            if not self.board.board[i-(x+1)][0].clicked and not self.board.board[i-(x+1)][0].flagged:
                candidates.append(i-(x+1))
        if not bottomEdge and not rightEdge:
            if not self.board.board[i+(x+1)][0].clicked and not self.board.board[i+(x+1)][0].flagged:
                candidates.append(i+(x+1))
        if not bottomEdge and not leftEdge:
            if not self.board.board[i+(x-1)][0].clicked and not self.board.board[i+(x-1)][0].flagged:
                candidates.append(i+(x-1))

        return candidates
    
    def getFlaggedTilesAroundTile(self,i,x,y):
        candidates = []
        rightEdge = False
        leftEdge = False
        topEdge = False
        bottomEdge = False

        if (i+1) <= x:
            topEdge = True
        if (i+1) % x == 0:
            rightEdge = True
        if i % x == 0:
            leftEdge = True
        if (i+1) > (y-1)*x:
            bottomEdge = True
        
        if not topEdge:
            if self.board.board[i-x][0].flagged:
                candidates.append(i-x)
        if not rightEdge:
            if self.board.board[i+1][0].flagged:
                candidates.append(i+1)
        if not leftEdge:
            if self.board.board[i-1][0].flagged:
                candidates.append(i-1)
        if not bottomEdge:
            if self.board.board[i+x][0].flagged:
                candidates.append(i+x)
        if not topEdge and not rightEdge:
            if self.board.board[i-(x-1)][0].flagged:
                candidates.append(i-(x-1))
        if not topEdge and not leftEdge:
            if self.board.board[i-(x+1)][0].flagged:
                candidates.append(i-(x+1))
        if not bottomEdge and not rightEdge:
            if self.board.board[i+(x+1)][0].flagged:
                candidates.append(i+(x+1))
        if not bottomEdge and not leftEdge:
            if self.board.board[i+(x-1)][0].flagged:
                candidates.append(i+(x-1))

        return sorted(set(candidates))

    #More Advanced Logic Checks For When Basic Ones Fail
    def advancedTileCheck(self,tile,x,y):
        #print("Tile: {}, x: {}, y: {}".format(tile,x,y))
        unknownTiles = self.getUnknownTilesAroundTile(tile,x,y)
        flaggedTiles = self.getFlaggedTilesAroundTile(tile,x,y)
        knownTiles = self.getKnownTilesAroundTile(tile,x,y)
        tilesAroundTile = self.getTilesAroundTile(tile,x,y)
        effectiveValue = self.getEffectiveValue(tile,flaggedTiles)
        #print("Tile {} with a value of {}".format(tile,effectiveValue))
         
        result = self.onEffectiveEdge(tile,x,y,unknownTiles,effectiveValue,tilesAroundTile)
        #print("result: {}".format(result))
        if result[0]:
            for child in result[1]:
                if child in knownTiles:
                    nonAffectedTiles = [i for i in self.getTilesAroundTile(child,x,y) if i not in tilesAroundTile]
                    nonAffectedTiles.pop(nonAffectedTiles.index(tile))
                    childEffectiveValue = self.getEffectiveValue(child,self.getFlaggedTilesAroundTile(child,x,y))
                    childTheoreticalValue = self.getTheoreticalValue(childEffectiveValue,self.getUnknownTilesAroundTile(child,x,y))
                    #print("childEffVal: {}".format(childEffectiveValue))
                    #print("childTheoVal: {}".format(childTheoreticalValue))
                    #print("nonAffectedTiles: {}".format(nonAffectedTiles))
                    if childEffectiveValue == effectiveValue:
                        #print("Revealing nonAffectedTiles with root tile of {}".format(tile))
                        for i in nonAffectedTiles:
                            self.board.board[i][0].reveal()
                            self.revealedMines += 1
                    elif childTheoreticalValue == effectiveValue:
                        for i in nonAffectedTiles:
                            #print("Flagging nonAffectedTiles with root tile of {}".format(tile))
                            if not self.board.board[i][0].flagged:
                                self.board.board[i][0].flag()
                        
            

    #Actual Value of Tile - Number of known mines around tile     
    def getEffectiveValue(self,tile,flaggedTiles):
        return self.board.board[tile][0].value - len(flaggedTiles)

    #Lack of better name
    #Number of Unknown Tiles - Effective Value
    def getTheoreticalValue(self,effectiveValue,unknownTiles):
        return len(unknownTiles) - effectiveValue
        
    #Returns T/F if the tile is on an effective edge
    def onEffectiveEdge(self,tile,x,y,unknownTiles,effectiveValue,tilesAroundTile):
        #Checks if tile is valid candidate for effective edge
        if self.getTheoreticalValue(effectiveValue,unknownTiles) != 1 and effectiveValue != 1:
            #print("Failed check 1, theoValue: {}".format(self.getTheoreticalValue(effectiveValue,unknownTiles)))
            return [False]
        """
        if effectiveValue != 1:
            print("Failed altcheck 1, effValue: {}".format(effectiveValue))
            return [False]
        """
        #Checks if at least 2 tiles are adjacent to each other
        adjacentTiles = False
        for i in unknownTiles:
            if i-1 in unknownTiles:
                adjacentTiles = True
            if i+1 in unknownTiles:
                adjacentTiles = True
            if i-x in unknownTiles:
                adjacentTiles = True
            if i+x in unknownTiles:
                adjacentTiles = True

        if adjacentTiles == False:
            #print("Failed check 2, unknownTiles: {}".format(unknownTiles))
            return [False]

        #Checks for a 3 long line of known/flagged tiles
        NSide = [tile-(x+1),tile-x,tile-(x-1)]
        WSide = [tile-(x+1),tile-1,tile+(x-1)]
        ESide = [tile-(x-1),tile+1,tile+(x+1)]
        SSide = [tile+(x-1),tile+x,tile+(x+1)]
        
        sides = [NSide,WSide,ESide,SSide]
        oppositeTileValues = [SSide[1],ESide[1],WSide[1],NSide[1]]
        
        KFAroundTiles = [tile for tile in tilesAroundTile if tile not in unknownTiles]
        #print("KFAroundTiles: {}".format(KFAroundTiles))
        
        validSides = []
        for side in sides:
            knownOrFlagged = [tile in KFAroundTiles for tile in side]
            #print("knownOrFlagged Phase 1: {}".format(knownOrFlagged))

            #Checks if tile is out of map
            for i in range(len(knownOrFlagged)):
                if side[i] not in tilesAroundTile:
                    knownOrFlagged[i] = True
            #print("knownOrFlagged: {}".format(knownOrFlagged))
            if False not in knownOrFlagged:
                validSides.append(side)

        validSides = [side for index,side in enumerate(validSides) if side not in validSides[:index]]
                    
        if len(validSides) != 0:
            #print("validSides: {}\noppositeTileValues: {}".format(validSides,oppositeTileValues))
            validOppositeTileValues = []
            for side in validSides:
                #print("side: {}".format(side))
                validOppositeTileValues.append(oppositeTileValues[sides.index(side)])
            return (True,validOppositeTileValues)
        
        #If sides check fails, return False
        return [False]
    
    #Returns N/S/E/W for the child relative to the root
    def determineSide(self,root,child,x,y):
        if child == root-1:
            return "W"
        if child == root+1:
            return "E"
        if child == root-x:
            return "N"
        if child == root+x:
            return "S"
        return "ERROR, Root: {}, Child: {}".format(root,child)

    def getTilesAroundTile(self,i,x,y):
        candidates = []
        rightEdge = False
        leftEdge = False
        topEdge = False
        bottomEdge = False

        if (i+1) <= x:
            topEdge = True
        if (i+1) % x == 0:
            rightEdge = True
        if i % x == 0:
            leftEdge = True
        if (i+1) > (y-1)*x:
            bottomEdge = True
        
        if not topEdge:
            candidates.append(i-x)
        if not rightEdge:
            candidates.append(i+1)
        if not leftEdge:
            candidates.append(i-1)
        if not bottomEdge:
            candidates.append(i+x)
        if not topEdge and not rightEdge:
            candidates.append(i-(x-1))
        if not topEdge and not leftEdge:
            candidates.append(i-(x+1))
        if not bottomEdge and not rightEdge:
            candidates.append(i+(x+1))
        if not bottomEdge and not leftEdge:
            candidates.append(i+(x-1))

        return candidates

    def getKnownTilesAroundTile(self,i,x,y):
        candidates = []
        rightEdge = False
        leftEdge = False
        topEdge = False
        bottomEdge = False

        if (i+1) <= x:
            topEdge = True
        if (i+1) % x == 0:
            rightEdge = True
        if i % x == 0:
            leftEdge = True
        if (i+1) > (y-1)*x:
            bottomEdge = True

        #print("i: {}, t: {}, r: {}, l: {}, d: {}".format(i,topEdge,rightEdge,leftEdge,bottomEdge))
        if not topEdge:
            tile = self.board.board[i-x][0]
            if tile.clicked and tile.value > 0 and not tile.flagged:
                candidates.append(i-x)
        if not rightEdge:
            tile = self.board.board[i+1][0]
            if tile.clicked and tile.value > 0 and not tile.flagged:
                candidates.append(i+1)
        if not leftEdge:
            tile = self.board.board[i-1][0]
            if tile.clicked and tile.value > 0 and not tile.flagged:
                candidates.append(i-1)
        if not bottomEdge:
            tile = self.board.board[i+x][0]
            if tile.clicked and tile.value > 0 and not tile.flagged:
                candidates.append(i+x)
        if not topEdge and not rightEdge:
            tile = self.board.board[i-(x-1)][0]
            if tile.clicked and tile.value > 0 and not tile.flagged:
                candidates.append(i-(x-1))
        if not topEdge and not leftEdge:
            tile = self.board.board[i-(x+1)][0]
            if tile.clicked and tile.value > 0 and not tile.flagged:
                candidates.append(i-(x+1))
        if not bottomEdge and not rightEdge:
            tile = self.board.board[i+(x+1)][0]
            if tile.clicked and tile.value > 0 and not tile.flagged:
                candidates.append(i+(x+1))
        if not bottomEdge and not leftEdge:
            tile = self.board.board[i+(x-1)][0]
            if tile.clicked and tile.value > 0 and not tile.flagged:
                candidates.append(i+(x-1))

        return candidates
    
    def cancelActiveJob(self):
        if self.job != None:
            self.after_cancel(self.job)
            self.job = None

class Board():
    def __init__(self,master,x=10,y=10,m=0.15):
        self.master = master
        x = min(35,max(3,x))
        y = min(25,max(1,y))
        self.m = m
        self.x = x
        self.y = y
        self.size = x*y
        self.mineCount = math.ceil(min((x*y)-1,max(1,(x*y)*m)))
        self.activeTiles = (x*y)-self.mineCount
        self.mineClicked = False
        
        self.generateBoard()
        self.initializeBoard()

    """
    Board Layout: [TileObject,x,y,isMine]
    """
    def generateBoard(self):
        #Playfield
        self.board = {}
        debugMode = False
        if debugMode:
            #30x15
            minePos = [False] * (self.x*self.y)
            minePos[4] = True
            minePos[90] = True
            minePos[121] = True
            minePos[154] = True
            minePos[65] = True
            minePos[95] = True
            minePos[152] = True

        else:
            minePos = [True]*self.mineCount + [False]*((self.x*self.y)-self.mineCount)
            random.shuffle(minePos)
        counter = 0
        for r in range(self.y):
            for c in range(self.x):
                if minePos[counter]:
                    self.board[counter] = [Tile(self.master,r,c,counter,True),c,r,minePos[counter]]
                else:
                    self.board[counter] = [Tile(self.master,r,c,counter,False),c,r,minePos[counter]]
                counter += 1

        #Other misc buttons
        self.statusText = tk.StringVar()
        self.statusText.set("Playing")
        self.buttonFont = tk.font.Font(size=15,weight="bold",family="Arial")

        self.playAgain = tk.Button(self.master,text="Play Again",bg="gray85",fg="black",command=lambda:game.setup(),font=self.buttonFont)
        self.statusLabel = tk.Label(self.master,textvariable=self.statusText,fg="gray30",font=self.buttonFont)
        self.solveButton = tk.Button(self.master,text="Solve",bg="gray85",fg="black",font=self.buttonFont,command=lambda:game.startSolve())

        self.playAgain.grid(row=self.y+1,column=0,columnspan=self.x//2)
        self.statusLabel.grid(row=0,columnspan=self.x)
        self.solveButton.grid(row=self.y+1,column=self.x//2,columnspan=self.x//2)
        
    def initializeBoard(self):
        for i in range(self.size):
            if not self.board[i][0].isMine:

                rightEdge = False
                leftEdge = False
                topEdge = False
                bottomEdge = False
                
                if (i+1) <= self.x:
                    topEdge = True
                if (i+1) % self.x == 0:
                    rightEdge = True
                if i % self.x == 0:
                    leftEdge = True
                if (i+1) > (self.y-1)*self.x:
                    bottomEdge = True

                #print("i: {}, t: {}, r: {}, l: {}, d: {}".format(i,topEdge,rightEdge,leftEdge,bottomEdge))
                count = 0
                if not topEdge:
                    if self.board[i-self.x][0].value == "M":
                        count += 1
                if not rightEdge:
                    if self.board[i+1][0].value == "M":
                        count += 1
                if not leftEdge:
                    if self.board[i-1][0].value == "M":
                        count += 1
                if not bottomEdge:
                    if self.board[i+self.x][0].value == "M":
                        count += 1
                if not topEdge and not rightEdge:
                    if self.board[i-(self.x-1)][0].value == "M":
                        count += 1
                if not topEdge and not leftEdge:
                    if self.board[i-(self.x+1)][0].value == "M":
                        count += 1
                if not bottomEdge and not rightEdge:
                    if self.board[i+(self.x+1)][0].value == "M":
                        count += 1
                if not bottomEdge and not leftEdge:
                    if self.board[i+(self.x-1)][0].value == "M":
                        count += 1

                self.board[i][0].value = count

    def spread(self,i):
        rightEdge = False
        leftEdge = False
        topEdge = False
        bottomEdge = False
        
        if (i+1) <= self.x:
            topEdge = True
        if (i+1) % self.x == 0:
            rightEdge = True
        if i % self.x == 0:
            leftEdge = True
        if (i+1) > (self.y-1)*self.x:
            bottomEdge = True
        
        if not topEdge:
            self.board[i-self.x][0].reveal()
        if not rightEdge:
            self.board[i+1][0].reveal()
        if not leftEdge:
            self.board[i-1][0].reveal()
        if not bottomEdge:
            self.board[i+self.x][0].reveal()
        if not topEdge and not rightEdge:
            self.board[i-(self.x-1)][0].reveal()
        if not topEdge and not leftEdge:
            self.board[i-(self.x+1)][0].reveal()
        if not bottomEdge and not rightEdge:
            self.board[i+(self.x+1)][0].reveal()
        if not bottomEdge and not leftEdge:
            self.board[i+(self.x-1)][0].reveal()

class Tile(tk.Button):
    def __init__(self,master,r,c,pos,mine):
        self.text = tk.StringVar()
        if mine:
            super().__init__(master,textvariable=self.text)
            self.value = "M"
        else:
            super().__init__(master,textvariable=self.text)
            self.value = -1
        self.configure(height=2,width=4,bg="RoyalBlue1")
        self.bind("<ButtonRelease-1>", self.reveal) 
        self.bind("<ButtonRelease-3>", self.flag)
        
        self.master = master
        self.clicked = False
        self.isMine = mine
        self.position = pos
        self.flagged = False

    def reveal(self,event=None):
        if not self.clicked and not self.flagged:
            self.clicked = True
            self.setFont()
            if not self.isMine:
                game.processClick(self.position,self.value)
                self.configure(bg="gray85")
            else:
                self.configure(bg="red")
                self.text.set(self.value)
                game.clickMine()

    def flag(self,event=None):
        if not self.clicked:
            tileFont = tk.font.Font(size=9,weight="bold",family="Arial")
            if not self.flagged:
                self.flagged = True
                self.text.set("F")
                self.configure(bg="yellow",font=tileFont,fg="black")
            else:
                self.flagged = False
                self.text.set("")
                self.configure(bg="RoyalBlue1")

    def setFont(self):
        colors = ["blue","green","red","dark blue","brown","cyan","black","gray50"]
        tileFont = tk.font.Font(size=9,weight="bold",family="Arial")
        if not self.isMine:
            self.configure(font=tileFont,fg=colors[self.value-1])
        else:
            self.configure(font=tileFont,fg="black")

root = tk.Tk()
game = Minesweeper(master=root)
game.mainloop()
