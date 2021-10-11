# Hexagonal Grid
import pygame, sys, pickle, time
try:
    from hexClasses import HexMap
    from botFunctions import blockBot
except:
    sys.exit()

def debugVisually(gamesList, specific=None):
    pygame.init()
    screen = pygame.display.set_mode((500, 600)) # Size of the screen
    screen.fill((255, 255, 255)) # Filling with white, must provide a tuple
    for index, newGame in enumerate(gamesList):
        if specific and index not in specific: continue
        status = None # Neither win nor loss
        num_rows = 11
        num_cols = 5
        hexSize = 30
        freeBlock = 2 # The pig moves after last block is placed down
        moves = 0

        main_map = HexMap(num_rows, num_cols, hexSize, newGame, all_vert, screen)

        while status == None:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    coord = main_map.pxl_to_double(pos)
                    pigCoord = main_map.pxl_to_double(main_map.pig.pos)
                    if coord not in main_map.tiles:
                        bestBlock, score = blockBot(main_map, 1, moves, freeBlock)
                        if score == 100: print("This Should Win...")
                        #print(f"Best: {bestBlock}")
                        if bestBlock == None or bestBlock == pigCoord:
                            status = "loss"
                            break
                        #moveList.append(bestBlock)
                        coord = bestBlock
                    blockAble = main_map.blockTile(coord)
                    if blockAble:
                        moves += 1
                        if freeBlock > 0:
                            freeBlock -= 1
                        else:
                            path = main_map.optimalPath(pigCoord, 1, set(), [], [[0]*(10)], moves<=4)
                            print(path)
                            playerWin = main_map.movePig(moves, path[0][1])
                            if playerWin==True:
                                #print(moveList)
                                status = "win"

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()
        print(status)
        if status=="loss": losses.append(index)
        time.sleep(.15)

def debugSilently(gamesList, specific=None):
    for index, newGame in enumerate(gamesList):
        if specific and index not in specific: continue
        status = None # Neither win nor loss
        num_rows = 11
        num_cols = 5
        hexSize = 30
        freeBlock = 2 # The pig moves after last block is placed down
        moves = 0
        main_map = HexMap(num_rows, num_cols, hexSize, newGame, all_vert, draw=False)
        while status == None:
            pigCoord = main_map.pig.pos
            bestBlock = blockBot(main_map, 1, moves, freeBlock)[0]
            if bestBlock == None or bestBlock == pigCoord:
                status = "loss"
                break
            blockAble = main_map.blockTile(bestBlock, draw=False)
            if blockAble:
                moves += 1
                if freeBlock > 0:
                    freeBlock -= 1
                else:
                    path = main_map.optimalPath(pigCoord, 1, set(), [], [[0]*(10)], moves<=4)
                    playerWin = main_map.movePig(moves, path[0][1], draw=False)
                    if playerWin:
                        status = "win"
        print(status)
        if status=="loss": losses.append(index)

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
    losses = []
    game = 't' # Not playing the game and wanting it visualized
    try:
        if game == 't':
            debugVisually(gamesList)
        else:
            debugSilently(gamesList)
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        pygame.quit()
    print(losses)
    sys.exit()
