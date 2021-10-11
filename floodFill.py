class FloodTree():
    def __init__(self):
        self.tree = []

    def removeUseless(self):
        pass

def floodFill(self, start, bound=None): # Good for the beginning 2 step->3 step; opt is max amount out you want to go
    distLook = {2: 4, 3: 4}
    fringes = [start] # THE NEW
    blockRange = {start: (None, set())}
    winCount = {}
    countRange = 3
    countTotal = 0
    opt = distLook.get(bound, bound) if bound else 10
    i = 1

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
