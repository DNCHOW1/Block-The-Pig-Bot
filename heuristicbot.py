import time
from collections import OrderedDict

class HeuristicBot():
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

    def returnWrapper(self, moves, gameState, pig_loc, bestBlock, bbScore):
        """
        Parameters:
            Current # of moves??
            Current gamestate
            Current pig location, assume it's double coord
            Tuple: (bestBlock, score_associated)
        Returns:
            Tuple: (bestBlock, score_associated)
        """
        # Converts the pig_loc from coord to int
        true_pig_loc = self.getTrueLoc(pig_loc)

        if (true_pig_loc, gameState) not in self.gameStateTest:
            self.gameStateTest[(true_pig_loc, gameState)] = (bestBlock, bbScore)
        return (bestBlock, bbScore)

    def blockMany(self, hexMap, moves, freeBlock, pig_pos, coord, score, dumbPath = True):
        scoreTotal = 0
        nextMoves = hexMap.optimalPath(coord, dumbPath and moves + 1 <= self.dumb_limit) # BEFORE, IT WAS: moves+1 <= 3
        if len(nextMoves) > 1:
            return -100
        for move in nextMoves:
            if not freeBlock: hexMap.movePig(moves+1, move)
            debug, potentialScore = self.blockBot(hexMap, moves+1, max(freeBlock-1, 0), hexMap.pig.pos, score, True)
            hexMap.pig.move(pig_pos)
            if potentialScore < 0:
                return -100
            scoreTotal += potentialScore
        return (scoreTotal / len(nextMoves))

    def blockBot(self, hexMap, moves, freeBlock, pig_pos, score=6, quie=False): # Instead of quie maybe depth? Start at 1, then when this called again it'll be 0##############################
        # Returns best tile bot can block currently
        # Edit score by evaluating current state

        coord = pig_pos
        if (possState := (self.getTrueLoc(coord), hexMap.gameState)) in self.gameStateTest:
            self.savedSteps += 1
            return self.gameStateTest[possState]

        maxScore = (None, -100)
        eval = self.evalPigWin(hexMap, coord, score, freeBlock)
        if eval:
            if eval[0] in hexMap.winningTiles and quie:
                prevGameState = hexMap.blockTile(eval[0])
                if self.pigDangerWin(hexMap, coord):
                    hexMap.unBlockTile(eval[0], prevGameState)
                    return self.returnWrapper(moves, hexMap.gameState, coord, None, -100)

                # Test the many pig options
                scoreAvg = self.blockMany(hexMap, moves, freeBlock, pig_pos, coord, score, False)
                hexMap.unBlockTile(eval[0], prevGameState)
                return self.returnWrapper(moves, hexMap.gameState, coord, eval[0], scoreAvg)
            return self.returnWrapper(moves, hexMap.gameState, coord, *eval)

        hexRange, impossiblePlayerWin = self.evalDanger(hexMap, coord, moves)
        if impossiblePlayerWin: return self.returnWrapper(moves, hexMap.gameState, coord, None, -100)

        possList, fastestWin = hexMap.floodFill(coord, override = freeBlock > 0)
        if fastestWin == 100 and not freeBlock: return self.returnWrapper(moves, hexMap.gameState, coord, None, 100)  # Immediate win, no winning path in site
        for hexC in (hexRange or possList):
            new_score, shortestStep = score, 2
            scoreAvg = 0
            prevGameState = hexMap.blockTile(hexC)
            if not freeBlock:
                # Do not evaluate win in beginning stage
                new_score, shortestStep = self.evalPlayWin(hexMap, coord, fastestWin)

            # Play out every possibility until an absolute win
            # Test the pig's multiple movement options
            if new_score != 100:
                scoreAvg = self.blockMany(hexMap, moves, freeBlock, pig_pos, coord, score=new_score)
            maxScore = max((hexC, scoreAvg or new_score), maxScore, key=lambda x: x[1])

            # Return to original game state
            hexMap.unBlockTile(hexC, prevGameState)
            if maxScore[1] == 100: break # Met win condition
        return self.returnWrapper(moves, hexMap.gameState, coord, *maxScore)

    def evalPlayWin(self, hexMap, coord, prevFastest):
        bound = prevFastest
        b, fastestWin = hexMap.floodFill(coord, bound)
        return (100, None) if fastestWin == 100 else (0, fastestWin)

    def evalPigWin(self, hexMap, pos, score, freeBlock): # Check if pig wins on next pig move
        if freeBlock: return None
        tile = hexMap.tiles[pos]
        possPigWin = [neighbor for neighbor in tile.neighbors.keys() if neighbor in hexMap.winningTiles]
        if possPigWin:
            # If possibleWins > 1, standing on danger tile; else, block tile but continue onwards
            return (pos, -100) if len(possPigWin) > 1 else (possPigWin[0], score) # Instead of score maybe it should be 100

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
