# Hexagonal Grid
import pygame, sys, random, pickle
from hexClasses import HexMap
from botFunctions import blockBot
#import copyMap

if __name__ == "__main__":
    gamesList = []
    with open('BlockThePig/allVertices.pkl', 'rb') as input:
        all_vert = pickle.load(input)
    with open('BlockThePig/realtime_map_data.pkl', 'rb') as input:
        tiles = pickle.load(input)

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
        main_map = HexMap(num_rows, num_cols, hexSize, tiles, all_vert, screen)

        running = True
        moveList = []
        while running and status == None:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    coord = main_map.pxl_to_double(pos)
                    pigCoord = main_map.pxl_to_double(main_map.pig.pos)
                    if coord not in main_map.tiles:
                        bestBlock, score = blockBot(main_map, 1, moves, freeBlock)
                        if score == 100: print("This Should Win...") # Memorize the
                        #print(f"Best: {bestBlock}")
                        if bestBlock == None or bestBlock == pigCoord:



                            # First 2 could've blocked the pig completely
                            # IMPORTANT, THINKS THAT IT IS LOSS
                            status = "loss"
                            break




                        moveList.append(bestBlock)
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
                                print(moveList)
                                status = "win"

                if event.type == pygame.QUIT:
                    running = False
            pygame.display.update()
        print(status)

    except Exception as e:
        print(f"Exception: {e}")
    finally:
        pygame.quit()
    sys.exit()
