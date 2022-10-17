import time
from collections import OrderedDict

from .bot import LOSS, Bot

class MinMaxBot(Bot):
    global WIN, LOSS
    WIN = 1
    LOSS = -1

    def returnWrapper(self, gameState, coord, bestBlock, bbScore):
        """
        Parameters:
            Current gamestate
            Current pig location, assume it's double coord
            Tuple: (bestBlock, score_associated)
        Returns:
            Tuple: (bestBlock, score_associated)
        """

        if (coord, gameState) not in self.gameStateTest:
            self.gameStateTest[(coord, gameState)] = (bestBlock, bbScore)
        return (bestBlock, bbScore)

    def blockMany(self, hexMap, moves, freeBlock, coord, score):
        nextMoves = hexMap.optimalPath(coord, moves + 1 <= self.dumb_limit)
        
        # Minmax Algorithm, attempting to find absolute win
        for move in nextMoves:
            if not freeBlock: hexMap.movePig(moves+1, move)
            _, result = self.blockBot(hexMap, moves+1, max(freeBlock-1, 0), hexMap.pig.pos, score, True)
            hexMap.pig.move(coord) # Return to original gameState
            if result < 0:
                return LOSS

        return WIN

    def blockBot(self, hexMap, moves, freeBlock, coord, score=6, quie=False): 
        # Returns best tile bot can block currently

        # Check to see if the current state has been seen before
        if (possState := (coord, hexMap.gameState)) in self.gameStateTest:
            self.savedSteps += 1
            return self.gameStateTest[possState]

        # If forcedBlock is in winningTiles then must immediately block, else pig already won
        maxScore = (None, LOSS)
        forcedBlock, evaluation = self.evalPigWin(hexMap, coord, score, freeBlock)
        if forcedBlock and evaluation:
            if forcedBlock in hexMap.winningTiles and quie:
                prevGameState = hexMap.blockTile(forcedBlock)
                if self.pigDangerWin(hexMap, coord):
                    hexMap.unBlockTile(forcedBlock, prevGameState)
                    return self.returnWrapper(hexMap.gameState, coord, None, LOSS)

                # Test the many pig options
                scoreAvg = self.blockMany(hexMap, moves, freeBlock, coord, score)
                hexMap.unBlockTile(forcedBlock, prevGameState)
                return self.returnWrapper(hexMap.gameState, coord, forcedBlock, scoreAvg)
            else:
                return self.returnWrapper(hexMap.gameState, coord, forcedBlock, evaluation)

        # Evaluate the danger tiles nearby, if too much player can't win
        dangerTiles, impossiblePlayerWin = self.evalDanger(hexMap, coord, moves)
        if impossiblePlayerWin: return self.returnWrapper(hexMap.gameState, coord, None, LOSS)

        possList, pigFastestWin = hexMap.floodFill(coord, override=freeBlock > 0)
        if pigFastestWin == 100 and not freeBlock: return self.returnWrapper(hexMap.gameState, coord, None, WIN)  # Immediate win, no winning path in site
        
        for hexC in (dangerTiles or possList):
            new_score = score
            scoreAvg = 0 
            prevGameState = hexMap.blockTile(hexC)

            # Do not evaluate win in beginning stage
            if not freeBlock:
                new_score = self.evalPlayWin(hexMap, coord, pigFastestWin)

            # Play out every possibility until an absolute win
            # Test the pig's multiple movement options
            if new_score != WIN:
                scoreAvg = self.blockMany(hexMap, moves, freeBlock, coord, score=new_score)
            maxScore = max((hexC, scoreAvg or new_score), maxScore, key=lambda x: x[1])

            # Return to original game state
            hexMap.unBlockTile(hexC, prevGameState)
            if maxScore[1] == WIN: break # Met win condition

        return self.returnWrapper(hexMap.gameState, coord, *maxScore)
