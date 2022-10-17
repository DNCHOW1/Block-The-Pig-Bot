import time
from collections import OrderedDict

# To act as a super class
class Bot:
    global LOSS, WIN
    LOSS = -1
    WIN = 1

    def __init__(self, dumb_limit):
        self.gameStateTest = {}
        self.savedSteps = 0
        self.dumb_limit = dumb_limit # How long the pig will be dumb (aka follow predictable pathing)

    def resetSavedStates(self):
        self.savedSteps = 0
        self.gameStateTest = {}

    def lengthSavedStates(self):
        return len(self.gameStateTest)

    def amtSaved(self):
        return self.savedSteps

    def getTrueLoc(self, pig_loc):
        row, col = pig_loc
        cond = row % 2
        return (row*5 + (col-cond)//2)

    def evalPlayWin(self, hexMap, coord, prevFastest):
        bound = prevFastest
        _, fastestWin = hexMap.floodFill(coord, bound)
        return WIN if fastestWin == 100 else LOSS # Player has won

    def evalPigWin(self, hexMap, pos, score, freeBlock): # Check if pig wins on next pig move
        # If freeBlock pig shouldn't move
        if freeBlock: 
            return (None, None)

        tile = hexMap.tiles[pos]
        possPigWin = [neighbor for neighbor in tile.neighbors.keys() if neighbor in hexMap.winningTiles]
        if possPigWin:
            # If possibleWins > 1, standing on danger tile; else, block tile but continue onwards
            return (pos, LOSS) if len(possPigWin) > 1 else (possPigWin[0], score) # Instead of score maybe it should be 100
        else:
            return (None, None)

    def evalDanger(self, hexMap, pos, moves):
        if moves <= 2: return (None, False)
        tile = hexMap.tiles[pos]
        dger = OrderedDict()
        count = 0
        for tileN, neighbor in self.dangerLoopHelper(hexMap, tile):
            winTiles = []
            for nX in tileN.neighbors.keys():
                if nX in hexMap.winningTiles and nX not in dger:
                    winTiles.append(nX)
                    count += 1
            if len(winTiles) >= 2:
                for hexC in winTiles+[neighbor]:
                    dger[hexC] = 1
        return (dger.keys(), count > 4 and moves > 4)

    def pigDangerWin(self, hexMap, pos):
        tile = hexMap.tiles[pos]
        for tileN, _ in self.dangerLoopHelper(hexMap, tile):
            winCount = sum((nX in hexMap.winningTiles) for nX in tileN.neighbors.keys())
            if winCount >= 2:
                return True
        return False

    def dangerLoopHelper(self, hexMap, tile):
        for neighbor in tile.neighbors.keys():
            if neighbor in hexMap.dangerTiles:
                tileN = hexMap.tiles[neighbor]
                yield (tileN, neighbor)
