from math import *
from collections import OrderedDict
from itertools import chain
import pickle, pygame

class Pig():
    def __init__(self, tile, size, screen, draw=True):
        self.pos = tile.getCP()
        if draw:
            self.rect = pygame.Rect(0, 0, size, size)
            self.rect.center = self.pos # Centers the canvas to draw on
            self.image = pygame.image.load("C:/Users/Dien Chau/Downloads/Pippa.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (size, size))
            self.erase = pygame.Surface((size, size)).convert()
            self.screen = screen
            self.erase.fill((255,255,255))
            self.screen.blit(self.image, self.rect) # Draws the image on the small canvas

    def move(self, point, draw=True):
        self.pos = point
        if draw:
            self.screen.blit(self.erase, self.rect) # Erases the current spot pig is in
            self.rect.center = point
            self.screen.blit(self.image, self.rect)

class Tile():
    def __init__(self, vertices, doubleCoord, blocked=False):
        self.neighbors = OrderedDict()
        self.blocked = blocked
        self.vert = vertices
        self.CP = vertices if doubleCoord else None # vertices will instead be tuple if doubleCoord

    def getCP(self):
        if not self.CP:
            avgX = sum(x for x,y in self.vert)/6
            avgY = sum(y for x,y in self.vert)/6
            self.CP = (avgX, avgY)
        return self.CP

    def __repr__(self):
        return f"{self.blocked}"

class HexMap():
    def __init__(self, rows, cols, size, tiles, all_vert, screen=None, draw=True):
        self.rows = rows
        self.cols = cols
        self.hexSize = size
        self.start = 500/3 # Sub 900 for screen width// FIX THIS TO CENTER
        self.tiles = {}    # Store hexmap coordinates as tuple (row, col)
        self.all_vert = all_vert
        self.winningTiles = set()
        self.dangerTiles = set()
        self.blockedTilesStack = []
        self.directions = ((0, -2), (-1, -1), (1, -1),
                           (0, 2), (-1, 1), (1, 1))
        self.screen = screen
        self.draw=draw


        if not tiles: # If blank dict
            self.initializeTilesGame()
        else:
            self.initializeTilesBot(tiles)
        if draw: self.drawGame()
        self.pig = Pig(self.tiles[(5, 5)], self.hexSize*7//6, self.screen, draw=self.draw)
        self.initializeNeighbors()

    def drawHexagon(self, boulder, points):
        fillHex = (128, 128, 128) if boulder else (255, 255, 255)
        pygame.draw.polygon(self.screen, fillHex, points) # Fill in a hexagon
        pygame.draw.polygon(self.screen, (0, 0, 0), points, 2) # Draw a boundary for the hexagon

    def drawGame(self):
        for tile in self.tiles.values():
            self.drawHexagon(boulder=False, points=tile.vert)
            if tile.blocked:
                self.drawHexagon(boulder=True, points=tile.vert)

    def initializeTilesBot(self, tiles):
        pigSeen = False
        for coord in tiles:
            row, col = coord
            cond = (row % 2)
            vertices = self.all_vert[row][col//2] if self.draw else coord
            self.tiles[coord] = Tile(vertices, vertices==coord, tiles[coord] and tiles[coord]!="p")
            self.initializeWinTiles(row, col, cond)
            '''
            DO LATER
            if tiles[coord] == "p":
                pigSeen = True
                self.pig = Pig(self.tiles[coord], self.hexSize*7//6, self.screen, draw=self.draw)
        if not pigSeen: self.pig = Pig(self.tiles[(5, 5)], self.hexSize*7//6, self.screen, draw=self.draw)'''

    def initializeTilesGame(self):
        # Initialize the 1st hexagon's vertices; ALso draws the map of hexagons
        points = []
        for i in range(1, 12, 2):
            points.append((self.start + self.hexSize + self.hexSize*cos(i*pi/6),
                                        self.hexSize + self.hexSize*sin(i*pi/6)))

        # Initialize spacing between hexagons
        self.spacingX = self.hexSize*cos(pi/6)
        self.spacingY = self.hexSize*sin(pi/6)+self.hexSize
        # Generate the grid of hexagons
        for row in range(self.rows):
            cond = (row % 2) # Is this a odd or even row; 0 is the row #; if it is "odd", no offset bc weird indexing
            # Generate the row of hexagons
            for col in range(cond, self.cols*2, 2):
                pts = [(int(x + col*self.spacingX), int(y + row*self.spacingY)) for x, y in points]
                self.tiles[(row, col)] = Tile(pts)
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
        for r,c in self.tiles.keys():
            tile = self.tiles[(r, c)]
            for i, j in self.directions:
                newR, newC = r+i, c+j
                if (newR, newC) in self.tiles and not self.tiles[(newR, newC)].blocked:
                    neighbor = self.tiles[(newR, newC)]
                    tile.neighbors[(newR, newC)] = 1

    def addNeighbors(self, r, c):
        previousAdjTiles = self.blockedTilesStack.pop()
        tile = self.tiles[(r, c)]
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

    def unBlockTile(self, point):
        if point in self.tiles:
            tile = self.tiles[point]
            if tile.blocked:
                tile.blocked = False
                self.addNeighbors(point[0], point[1])
            else:
                print("Trying to unblock unblocked Tile")

    def blockTile(self, point, draw=True):
        # If successful, return True. If not, pig can't move yet
        if point in self.tiles:
            tile = self.tiles[point]
            if not tile.blocked and self.pig.pos!=tile.getCP():
                tile.blocked = True
                if draw: self.drawHexagon(boulder=True, points=tile.vert)
                self.removeNeighbors(point[0], point[1])
                return self
            else:
                if tile.blocked: print("Already Blocked")
                elif self.pig.pos == tile.getCP(): print("Pig Present")

    #
    #
    # Instead of movePig determining win, have blockBot function return bestBlock's after winning Paths
    # If dict is empty, then it is a win!
    def movePig(self, moves, optimalHex, draw=True): # Add another parameter; if simulate, then don't update pig position
        if optimalHex!=0: # Pig still has moves
            tile = self.tiles[optimalHex]
            self.pig.move(tile.getCP(), draw) # Move this elsewhere???
        else: # Player wins
            return True

    # Have another floodFill instead, this time to get all the optimal paths
    def optimalPath(self, coord, steps, visited, path, all_paths, notRand): # Where rand changes after a few moves in game;
                                                                            # pig no longer follows direction arr
        path_copy = path.copy()
        path_copy.append(coord)
        visit_copy = visited.copy()
        visit_copy.add(coord)
        tile = self.tiles[coord]
        visit_copy.update(tile.neighbors.keys())
        for neighbor in tile.neighbors.keys():
            if not all_paths or (all_paths and steps+1 <= len(all_paths[-1])-notRand):
                if neighbor not in visited:
                    if neighbor in self.winningTiles:
                        new_path = path_copy + [neighbor]
                        if len(new_path)!=len(all_paths[-1]):
                            while all_paths: all_paths.pop()
                        all_paths.append(path_copy+[neighbor])
                        continue
                    self.optimalPath(neighbor, steps+1, visit_copy, path_copy, all_paths, notRand)
            else:
                return all_paths
        return all_paths


    def floodFill(self, start, bound=None): # Good for the beginning 2 step->3 step; opt is max amount out you want to go
        distLook = {2: 4, 3: 4}
        fringes = [start] # THE NEW
        blockRange = {start: (None, set())}
        winCount = {}
        countRange = 3
        countTotal = 0
        opt = distLook.get(bound, bound) if bound else 10
        i = 1
        def checkBranch(hexC, stepL, countTotal):
            try:
                prev, validMoves = blockRange[hexC]
                while len(validMoves)==0:
                    del blockRange[hexC]
                    countTotal -= 1 if stepL <= countRange else 0
                    if prev == None:
                        break
                    prev2, validMoves = blockRange[prev]
                    if prev2 == None:
                        break
                    validMoves.remove(hexC)
                    hexC, prev = prev, prev2
                    stepL -= 1
                return countTotal
            except:
                print("Error in FloodFill")
        while i <= opt:
            temp = []
            for hexC in fringes:
                if hexC not in self.winningTiles:
                    tile = self.tiles[hexC] # Where path[-1] is the last coord arrived at
                    for neighbor in tile.neighbors.keys():
                        if neighbor not in blockRange:
                            # Affect temp here
                            countTotal += 1 if i <= countRange else 0
                            blockRange[hexC][1].add(neighbor)
                            if i != opt: blockRange[neighbor] = (hexC, set())
                            temp.append(neighbor)
                        if neighbor in self.winningTiles:
                            opt = distLook.get(i, i) if opt == 10 else opt
                            if i in winCount or len(winCount) != 2:
                                winCount[i] = winCount.get(i, 0) + 1
                    countTotal = checkBranch(hexC, i-1, countTotal)
            fringes = temp
            i+=1
        #if len(winCount) == 1: winCount[100] = 0
        if start in blockRange: del blockRange[start]
        return (blockRange.keys(), winCount, countTotal)

    def pxl_to_double(self, point):
        x, y = point
        return self.pxl_to_hex(x - (self.start + self.hexSize), y - self.hexSize)

    def pxl_to_hex(self, x, y):
        c = ((sqrt(3)*x/3) - y/3)/self.hexSize
        r = (2*y/3)/self.hexSize
        return self.cube_round(c, -c-r, r)

    def cube_round(self, x, y, z):
        rx, ry, rz = int(round(x)), int(round(y)), int(round(z))
        xDiff, yDiff, zDiff = abs(x-rx), abs(y-ry), abs(z-rz)

        if xDiff > yDiff and xDiff > zDiff:
            rx = -ry-rz
        elif yDiff > zDiff:
            ry = -rx-rz
        else:
            rz = -rx-ry
        return self.cube_to_double(rx, ry, rz)

    def cube_to_double(self, x, y, z):
        c = 2*x + z
        r = z
        return (r, c)
