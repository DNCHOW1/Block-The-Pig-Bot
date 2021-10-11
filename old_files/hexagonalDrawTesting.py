# Hexagonal Grid
from math import *
from copy import deepcopy
from collections import OrderedDict
from itertools import chain
import pygame, sys, random, pickle
#import copyMap
megaD = 0
class Pig():
    def __init__(self, tile, size, draw=True):
        self.pos = tile.getCP()
        if draw:
            self.rect = pygame.Rect(0, 0, size, size)
            self.rect.center = self.pos # Centers the canvas to draw on
            self.image = pygame.image.load("C:/Users/Dien Chau/Downloads/Pippa.png")
            self.image = pygame.transform.scale(self.image, (size, size))
            self.erase = pygame.Surface((size, size))
            self.erase.fill((255,255,255))
            screen.blit(self.image, self.rect) # Draws the image on the small canvas

    def move(self, point, draw=True):
        self.pos = point
        if draw:
            screen.blit(self.erase, self.rect) # Erases the current spot pig is in
            self.rect.center = point
            screen.blit(self.image, self.rect)

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

    def getInfo(self):
        return f"{self.blocked}, {self.neighbors}"

    def __repr__(self):
        return f"{self.blocked}, {self.neighbors}"

class HexMap():
    def __init__(self, rows, cols, size, tiles, draw=True):
        self.rows = rows
        self.cols = cols
        self.hexSize = size
        self.start = 500/3 # Sub 900 for screen width// FIX THIS TO CENTER
        self.tiles = {}    # Store hexmap coordinates as tuple (row, col)
        self.winningTiles = set()
        self.dangerTiles = set()
        self.directions = [[0, -2], [-1, -1], [1, -1],
                           [0, 2], [-1, 1], [1, 1]]
        self.draw=draw

        if not tiles: # If blank dict
            self.initializeTilesGame()
        else:
            self.initializeTilesBot(tiles)
        if draw: self.drawGame()
        self.initializeNeighbors()

    def __repr__(self):
        ret = ""
        for i, v in self.tiles.items():
            ret += f"{i}: {v.getInfo()}\n"
        return ret

    def drawGame(self):
        for tile in self.tiles.values():
            pygame.draw.polygon(screen, (0, 0, 0), tile.vert, 2) # Draw a boundary for hexagon
            if tile.blocked:
                self.drawBoulder(tile.vert)

    def initializeTilesBot(self, tiles):
        pigSeen = False
        for coord in tiles:
            row, col = coord
            cond = (row % 2)
            vertices = all_vert[row][col//2] if self.draw else coord
            self.tiles[coord] = Tile(vertices, vertices==coord, tiles[coord] and tiles[coord]!="p")
            if tiles[coord] == "p":
                pigSeen = True
                self.pig = Pig(self.tiles[coord], self.hexSize*7//6, draw=self.draw)
            self.initializeWinTiles(row, col, cond)
        if not pigSeen: self.pig = Pig(self.tiles[(5, 5)], self.hexSize*7//6, draw=self.draw)

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
                self.tiles[(row, col)] = Tile(pts, False)
                self.initializeWinTiles(row, col, cond)
        self.pig = Pig(self.tiles[(5, 5)], self.hexSize*7//6, draw=self.draw)

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

    def removeNeighbors(self, r, c):
        """Remove current tile from all nearby neighbors hash maps
           Neighbors -> tile is None because tile is blocked(inaccessible)"""
        tile = self.tiles[(r, c)]
        for coord in tile.neighbors.keys():
            neighbor = self.tiles[coord]
            neighbor.neighbors.pop((r, c))

    def unBlockTile(self, point):
        if point in self.tiles:
            tile = self.tiles[point]
            if tile.blocked:
                tile.blocked = False
                for coord in tile.neighbors.keys():
                    neighbor = self.tiles[coord]
                    neighbor.neighbors[point] = 1
                    neighbor.neighbors = OrderedDict(sorted(neighbor.neighbors.items()))
                pygame.draw.polygon(screen, (200, 255, 255), tile.vert) # Fill in a hexagon
                pygame.draw.polygon(screen, (0, 0, 0), tile.vert, 2) # Draw a boundary for the hexagon
            else:
                print("Not blocked")
        else:
            print("Not in range")

    def blockTile(self, point, draw=True):
        # If successful, return True. If not, pig can't move yet
        if point in self.tiles:
            tile = self.tiles[point]
            if not tile.blocked and self.pig.pos!=tile.getCP():
                tile.blocked = True
                if draw: self.drawBoulder(tile.vert)
                self.removeNeighbors(point[0], point[1])
                return self
            else:
                if tile.blocked: print("Already Blocked")
                elif self.pig.pos == tile.getCP(): print("Pig Present")

    def drawBoulder(self, points):
        pygame.draw.polygon(screen, (128, 128, 128), points) # Fill in a hexagon
        pygame.draw.polygon(screen, (0, 0, 0), points, 2) # Draw a boundary for the hexagon

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

    # Implement A* instead with a pig's winning tile being the target goal
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
        distLook = {2: 3, 3: 4}
        fringes = [start] # THE NEW
        blockRange = {start: (None, set())}
        winCount = {}
        countRange = 3
        countTotal = 0
        opt = distLook.get(bound, bound) if bound else 10
        i = 1
        def checkBranch(hexC, stepL, countTotal):
            prev, validMoves = blockRange[hexC]
            while len(validMoves)==0:
                del blockRange[hexC]
                countTotal -= 1 if stepL <= countRange else 0
                prev2, validMoves = blockRange[prev]
                if prev2 == None:
                    break
                validMoves.remove(hexC)
                hexC, prev = prev, prev2
                stepL -= 1
            return countTotal

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
        if len(winCount) == 1: winCount[100] = 0


        del blockRange[start]
        return (blockRange.keys(), winCount, countTotal)

    def pxl_to_double(self, point):
        x, y = point
        return self.pxl_to_hex(x - (self.start + self.hexSize), y - self.hexSize)

    def pxl_to_hex(self, x, y):
        c = ((sqrt(3)*x/3) - y/3)/hexSize
        r = (2*y/3)/hexSize
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







def blockBot(hexMap, depth, moves, freeBlock, score=6, quie=False): # Instead of quie maybe depth? Start at 1, then when this called again it'll be 0##############################
    # Returns best tile bot can block currently
    # Edit score by evaluating current state
    pig_pos = hexMap.pig.pos
    coord = hexMap.pxl_to_double(pig_pos) if hexMap.draw else pig_pos
    maxScore = [None, -6]
    hexRange = None
    #if not freeBlock: # At the beginning, only consider tiles in 3 block radius bc pig can't move
    eval = evalWinning(hexMap, coord, score, freeBlock)
    if eval:
        if eval[0] in hexMap.winningTiles and quie:
            #print(f"Quiet {eval[0]}")
            hexMap.blockTile(eval[0], draw=False)
            if evalDanger(hexMap, coord, moves+1, True):
                #hexMap.unBlockTile(eval[0])
                return [None, -100]

            # Test the many pig options???
            path = hexMap.optimalPath(coord, 1, set(), [], [[0]*(10)], moves+1<=4)
            if not freeBlock: hexMap.movePig(moves+1, path[0][1], draw=False)
            ret = blockBot(hexMap, depth, moves+1, freeBlock, score, quie=True)
            #hexMap.unBlockTile(eval[0])
            return ret
        return eval
    if moves > 2:
        hexRange, imposs = evalDanger(hexMap, coord, moves)
        if imposs: return [None, -100] # Override hexRange and imposs if immediate left win,
                                       # ORRRR, if next move won't be dangerTile

    possList, winCountB, tilesB = hexMap.floodFill(coord)
    if len(winCountB) == 0: return [None, 100]  # Immediate win, no winning path in site
    for hexC in (hexRange or possList):
        current = deepcopy(hexMap.tiles)
        futScoreAvg = 0
        # Copy the game state
        hexMap.blockTile(hexC, draw=False)
        new_score, uselessBlock, shortestStep = scoreTile(hexMap, coord, score, winCountB, tilesB, max(freeBlock-1, 0)) # Get the new score for blockBot
        #print(hexC, new_score, depth, maxScore, winCountB)

        # Allowing
        if (depth >= 1 or shortestStep==2) and new_score!=100 and not uselessBlock:
            # Test the pig's multiple movement options
            current2 = deepcopy(hexMap.tiles)
            seen = set()
            paths = hexMap.optimalPath(coord, 1, set(), [], [[0]*(shortestStep+2)], moves+1<=4)
            for path in paths:
                if path[1] not in seen:
                    seen.add(path[1])
                    if not freeBlock: hexMap.movePig(moves+1, path[1], draw=False)
                    debug, potScore = blockBot(hexMap, depth-1, moves+1, max(freeBlock-1, 0), new_score, True)
                    hexMap.tiles = current2
                    hexMap.pig.move(pig_pos, False)
                    #print(f"\nCP{coord}, Blocking{hexC}: DIR{path[1]}, {potScore}, {hexMap.tiles}\n")
                    if potScore < 0:
                        futScoreAvg = -100
                        break
                    futScoreAvg += potScore
            futScoreAvg /= len(seen)
        #print("out")
        if not uselessBlock: maxScore = max([hexC, futScoreAvg or new_score], maxScore, key=lambda x: x[1])

        # Return to original game state
        #hexMap.unBlockTile(hexC)
        hexMap.tiles = current
        if maxScore[1] == 100: break # Met win condition
    return maxScore

def blockFreeBlock(hexMap, freeBlock):
    if freeBlock:
        pass
    else:
        return False

# Another function for the loops and the scoring; Instead of holding the loop, hold the contents?
def scoreTile(hexMap, coord, score, winCountB, tilesB, freeBlock):
    # BIGGGGGGGGGGGGGGGGGGG: Have scoring scale left/right, 1 optimal path or not
    ret = None
    opt, opt2 = sorted(winCountB.keys())
    bound = opt if opt2 == 100 else opt2
    b, winCountA, tilesA = hexMap.floodFill(coord, bound)
    bigDiff = winCountB.get(opt,0)-winCountA.get(opt,0)
    smallDiff = winCountB.get(opt2,0)-winCountA.get(opt2,0)
    tDiff = tilesB-tilesA
    debug = (pow(4, -bigDiff) + pow(2, -smallDiff) + pow(3/2, -tDiff))
    func = score - debug
    func = score - (pow(4, -bigDiff) + pow(2, -smallDiff) + pow(3/2, -tDiff)) # Values and function(exponential) subject to change
    #print(func, bigDiff, smallDiff, tDiff, winCountB, winCountA)
    if not winCountA: func=100
    else: ret, _ = winCountA
    return (func, tDiff==1 and not bigDiff and not smallDiff, ret)

def evalWinning(hexMap, pos, score, freeBlock): # Check if player won on this pig move
    if freeBlock: return None
    tile = hexMap.tiles[pos]
    possWin = [neighbor for neighbor in tile.neighbors.keys() if neighbor in hexMap.winningTiles]
    if possWin:
        if len(possWin) > 1: # Currently standing on a dangerTile
            return [pos, -100]
        return [possWin[0], score]

def evalDanger(hexMap, pos, moves, determineDanger=False):
    tile = hexMap.tiles[pos]
    dger = set()
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
                dger.update(winTiles)
                dger.add(neighbor)
    return (dger, count > 4 and moves > 4) if not determineDanger else False

if __name__ == "__main__":
    gamesList = []
    with open('BlockThePig/allVertices.pkl', 'rb') as input:
        all_vert = pickle.load(input)
    with open('BlockThePig/multiple_map_data.pkl', 'rb') as input:
        while input:
            try:
                gamesList.append(pickle.load(input))
            except EOFError:
                break

    try:
        status = None # Neither win nor loss
        num_rows = 11
        num_cols = 5
        hexSize = 30
        freeBlock = 2 # The pig moves after last block is placed down
        moves = 0

        pygame.init()
        screen = pygame.display.set_mode((500, 600)) # Size of the screen
        screen.fill((255, 255, 255)) # Filling with white, must provide a tuple
        main_map = HexMap(num_rows, num_cols, hexSize, {})

        running = True
        #moveList = []
        while running and status == None:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    coord = main_map.pxl_to_double(pos)
                    pigCoord = main_map.pxl_to_double(main_map.pig.pos)
                    '''if coord not in main_map.tiles:
                        bestBlock, score = blockBot(main_map, 1, moves, freeBlock)
                        if score == 100: print("This Should Win...")
                        #print(f"Best: {bestBlock}")
                        if bestBlock == None or bestBlock == pigCoord:
                            status = "loss"
                            break
                        #moveList.append(bestBlock)
                        coord = bestBlock'''

                    if event.button == 1:
                        blockAble = main_map.blockTile(coord)
                        if blockAble:
                            moves += 1
                            if freeBlock > 0:
                                freeBlock -= 1
                            else:
                                path = main_map.optimalPath(pigCoord, 1, set(), [], [[0]*(10)], moves<=4)
                                playerWin = main_map.movePig(moves, path[0][1])
                                if playerWin==True:
                                    status = "win"
                    elif event.button == 2:
                        print(main_map)
                    elif event.button == 3:
                        main_map.unBlockTile(coord)

                if event.type == pygame.QUIT:
                    running = False
            pygame.display.update()
        print(status)
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        pygame.quit()
    sys.exit()
