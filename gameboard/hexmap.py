from math import *
from collections import OrderedDict
import pygame

from .pig import Pig
from .tile import Tile

class HexMap():
    def __init__(self, rows, cols, tiles, locs):
        self.rows = rows
        self.cols = cols
        self.tiles = {}
        self.winningTiles = set()
        self.dangerTiles = set()
        self.blockedTilesStack = []
        self.gameState = 0

        self.initializeTilesBot(tiles, locs)
        self.initializeGameState()
        self.pig = Pig(self.tiles[(5, 5)])
        self.initializeNeighbors()

    def convert_int_or_bits(self, input, isBits=True, debug=False):
        if isBits:
            if not self.tiles[input].blocked: raise Exception("isBits and blocked")
            row, col = input
            cond = row % 2
            return self.tiles[input].blocked << (row*5 + (col-cond)//2)
        else: # input is an integer 0-54 inclusive that needs to be converted to bits
            row = input // 5
            col = input % 5
            cond = row % 2
            return (self.tiles[(row, col*2 + cond)].blocked << input)

    def initializeGameState(self):
        for i in range(55):
            if i != 27:
                bitmask = self.convert_int_or_bits(i, isBits=False)
                self.gameState |= bitmask

    def initializeTilesBot(self, tiles, locs):
        pigSeen = False
        for coord in tiles:
            row, col = coord
            cond = (row % 2)
            self.tiles[coord] = Tile(coord, locs[coord], tiles[coord] and tiles[coord]!="p")
            self.initializeWinTiles(row, col, cond)

    def initializeWinTiles(self, row, col, cond):
        if row==0 or row==self.rows-1:
            self.winningTiles.add((row, col))
        elif col==0 or col==cond or col>=self.cols*2-2:
            self.winningTiles.add((row, col))

        if (row==1 or row==self.rows-2) and (col!=cond and col!=self.cols*2-cond):
            self.dangerTiles.add((row, col))
        elif (row!=0 and row!=self.rows-1) and (col==2 or col==7):
            self.dangerTiles.add((row, col))

    def initializeNeighbors(self):
        directions = ((0, -2), (-1, -1), (1, -1),
                           (0, 2), (-1, 1), (1, 1))
        for r,c in self.tiles.keys():
            tile = self.tiles[(r, c)]
            for i, j in directions:
                newR, newC = r+i, c+j
                if (newR, newC) in self.tiles and not self.tiles[(newR, newC)].blocked:
                    tile.neighbors[(newR, newC)] = 1

    def addNeighbors(self, r, c):
        previousAdjTiles = self.blockedTilesStack.pop()
        for coord, neighborsDict in previousAdjTiles:
            self.tiles[coord].neighbors = neighborsDict

    def removeNeighbors(self, r, c):
        """Remove current tile from all nearby neighbors hash maps
           Neighbors -> tile is None because tile is blocked(inaccessible)"""
        tile = self.tiles[(r, c)]
        memoNeighbors = []
        for coord in tile.neighbors.keys():
            neighbor = self.tiles[coord]
            memoNeighbors.append((coord, neighbor.neighbors.copy()))
            neighbor.neighbors.pop((r, c))
        self.blockedTilesStack.append(memoNeighbors)

    def unBlockTile(self, point, prevState):
        if point in self.tiles:
            tile = self.tiles[point]
            if tile.blocked:
                tile.blocked = False
                self.gameState = prevState
                self.addNeighbors(point[0], point[1])
            else:
                print("Trying to unblock non-blocked Tile")

    def blockTile(self, point, debug=False):
        # If successful, return True. If not, pig can't move yet
        # Update the gamestate, and have unblockTile reverse
        if point in self.tiles:
            tile = self.tiles[point]
            if not tile.blocked and self.pig.pos!=tile.getCP():
                stateToRet = self.gameState # If unblocked later, this will be what it returns to
                tile.blocked = True
                self.gameState |= self.convert_int_or_bits(point, isBits=True, debug=debug)
                self.removeNeighbors(point[0], point[1])
                return stateToRet
            else:
                if tile.blocked: print("Already Blocked")
                elif self.pig.pos == tile.getCP(): print("Pig Present")

    def movePig(self, moves, optimalHex): # Add another parameter; if simulate, then don't update pig position
        if optimalHex!=0: # Pig still has moves
            tile = self.tiles[optimalHex]
            self.pig.move(tile.getCP())
        else: # Player wins
            return True

    def bfsHelper(self, parentTree, viableTiles, curr, currLevel):
        # Function modifies viableTiles using parentTree
        while currLevel > 0 and curr not in viableTiles:
            viableTiles[curr] = currLevel
            curr = parentTree[curr] # This gets the parent and sets curr to parent
            currLevel -= 1

    def loopHelper(self, fringes, parentTree):
        for hexC in fringes: # Parent from the last block distance
            tile = self.tiles[hexC] # Where path[-1] is the last coord arrived at
            for neighbor in tile.neighbors.keys():
                if neighbor not in parentTree:
                    parentTree[neighbor] = hexC
                    yield neighbor

    def optimalPath(self, coord, notRand): # Should've probably be placed in the pig class
        parentTree = {coord: None}
        fringes = [coord]
        viableMoves = {coord: 0} # to be returned
        maxDist = 11
        i = 1

        while i <= maxDist:
            temp = []
            for neighbor in self.loopHelper(fringes, parentTree):
                if neighbor in self.winningTiles:
                    maxDist = i
                    self.bfsHelper(parentTree, viableMoves, neighbor, i)
                    if notRand: break
                else:
                    temp.append(neighbor)
            fringes = temp # If viableBlocks, then fringes contains winningTiles.
                           # Traverse through array and check if winning, then add the path
            i += 1
        # print(viableMoves)
        if len(viableMoves) == 1: return [0]
        viableMovesTwoDist = [k for k, v in viableMoves.items() if v == 2]
        # print(viableMovesTwoDist)
        ret = set()
        for neighbor in self.tiles[coord].neighbors.keys():
            for moveTwoDist in viableMovesTwoDist:
                if moveTwoDist in self.tiles[neighbor].neighbors: ret.add(neighbor)
        return list(ret)

    def floodFill(self, start, bound = 11, override = False): # Good for the beginning 2 step->3 step; maxDist is max amount out you want to go
        distLook = {2: 4, 3: 4}
        # If the distance is greater than 4, then just do the 1st block you see
        parentTree = {start: None}
        fringes = [start]
        viableBlocks = {start: 0} # to be returned
        fastestWin = 100
        maxDist = distLook.get(bound, bound) if override == False else 3
        i = 1

        while i <= maxDist:
            temp = []
            for neighbor in self.loopHelper(fringes, parentTree):
                if neighbor in self.winningTiles: # Indenting this makes 33 test cases run faster
                    maxDist = min(distLook.get(i, i), maxDist)
                    fastestWin = min(fastestWin, i)
                    self.bfsHelper(parentTree, viableBlocks, neighbor, i)
                else:
                    temp.append(neighbor)

            fringes = temp # If viableBlocks, then fringes contains winningTiles.
                           # Traverse through array and check if winning, then add the path
            i += 1

        ret = (k for k, v in sorted(viableBlocks.items(), key=lambda x: x[1]) if v != 0)
        return (ret, fastestWin) # If pathfind and still reaches this line, pig had no viable path to the end
