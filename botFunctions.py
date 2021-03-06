import time
from collections import OrderedDict

timelimit = .05

def blockMany(hexMap, depth, moves, freeBlock, pig_pos, coord, timeStart, score):
    scoreTotal = 0
    nextMoves = hexMap.optimalPath(coord, moves+1<=4)
    for move in nextMoves:
        if not freeBlock: hexMap.movePig(moves+1, move, draw=False)
        debug, potentialScore = blockBot(hexMap, depth-1, moves+1, max(freeBlock-1, 0), hexMap.pig.pos, timeStart, score, True)
        hexMap.pig.move(pig_pos, False)
        if potentialScore < 0:
            return -100
        scoreTotal += potentialScore
    return (scoreTotal / len(nextMoves))

def blockBot(hexMap, depth, moves, freeBlock, pig_pos, timeStart=None, score=6, quie=False): # Instead of quie maybe depth? Start at 1, then when this called again it'll be 0##############################
    # Returns best tile bot can block currently
    # Edit score by evaluating current state
    if timeStart and time.time() - timeStart >= timelimit: return (None, -100)
    coord = hexMap.pxl_to_double(pig_pos) if hexMap.draw else pig_pos
    maxScore = (None, -6)
    eval = evalWinning(hexMap, coord, score, freeBlock)
    if eval:
        if eval[0] in hexMap.winningTiles and quie:
            hexMap.blockTile(eval[0], draw=False)
            if evalDanger(hexMap, coord, moves+1, True):
                hexMap.unBlockTile(eval[0])
                return (None, -100)

            # Test the many pig options
            scoreAvg = blockMany(hexMap, depth, moves, freeBlock, pig_pos, coord, timeStart, score)
            hexMap.unBlockTile(eval[0])
            return (None, scoreAvg)
        return eval

    hexRange, imposs = evalDanger(hexMap, coord, moves)
    if imposs: return (None, -100)

    possList, fastestWin = hexMap.floodFill(coord)
    if fastestWin == 100 and not freeBlock: return (None, 100)  # Immediate win, no winning path in site
    for hexC in (hexRange or possList):
        if timeStart and time.time() - timeStart >= timelimit: return maxScore
        new_score, shortestStep = score, 2
        scoreAvg = 0
        hexMap.blockTile(hexC, draw=False)
        if not freeBlock: new_score, shortestStep = evalPlayWin(hexMap, coord, score, fastestWin, max(freeBlock-1, 0)) # Get the new score for blockBot

        # Play out every possibility until an absolute win
        if (depth >= 1 or shortestStep==2) and new_score!=100:
            # Test the pig's multiple movement options
            scoreAvg = blockMany(hexMap, depth, moves, freeBlock, pig_pos, coord, timeStart=time.time() if (depth == 1 and not quie) else None, score=new_score)
        maxScore = max((hexC, scoreAvg or new_score), maxScore, key=lambda x: x[1])

        # Return to original game state
        hexMap.unBlockTile(hexC)
        if maxScore[1] == 100: break # Met win condition
    return maxScore

def evalPlayWin(hexMap, coord, score, prevFastest, freeBlock):
    bound = prevFastest
    b, fastestWin = hexMap.floodFill(coord, bound)
    return (100, None) if fastestWin == 100 else (0, fastestWin)

def evalWinning(hexMap, pos, score, freeBlock): # Check if pig wins on next pig move
    if freeBlock:
        return None
    tile = hexMap.tiles[pos]
    possWin = [neighbor for neighbor in tile.neighbors.keys() if neighbor in hexMap.winningTiles]
    if possWin:
        # If possibleWins > 1, standing on danger tile; else, just block tile
        return (pos, -100) if len(possWin) > 1 else (possWin[0], score)

def evalDanger(hexMap, pos, moves, determineDanger=False):
    if moves <= 2: return (None, False)
    tile = hexMap.tiles[pos]
    dger = OrderedDict()
    count = 0
    for neighbor in tile.neighbors.keys():
        if neighbor in hexMap.dangerTiles:
            tileN = hexMap.tiles[neighbor]
            winTiles = []
            for nX in tileN.neighbors.keys():
                if nX in hexMap.winningTiles and nX not in dger:
                    winTiles.append(nX)
                    count += 1
            if len(winTiles) >= 2:
                if determineDanger: return True
                for hexC in winTiles+[neighbor]:
                    if hexC not in dger:
                        dger[hexC] = 1
    return (dger.keys(), count > 4 and moves > 4) if not determineDanger else False
