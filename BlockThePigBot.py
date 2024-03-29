# Hexagonal Grid
import sys, random, pickle, pyautogui, time
from gameboard import HexMap
from bots import HeuristicBot, MinMaxBot
from copyMap import captureNewGame, captureNewPigCV, hitContinueCV # There should be functions here instead

def pigCaptureHelper(main_map, path):
    tile_list = [main_map.tiles[doubleCoord] for doubleCoord in path]

    tile_list = []
    maxx = maxy = -1
    minx = miny = 5000
    for doubleCoord in path:
        pixX, pixY = main_map.tiles[doubleCoord].getPixelCoord()
        minx = min(minx, pixX)
        miny = min(miny, pixY)
        maxx = max(maxx, pixX)
        maxy = max(maxy, pixY)
        tile_list.append(main_map.tiles[doubleCoord])
    return minx-100, miny-100, maxx+100, maxy+50, tile_list

def main():
    time.sleep(2)
    round = 1
    bot = MinMaxBot(3)
    while True:
        print(f"==================== Round {round} ========================")
        tiles, locs = captureNewGame()
        num_rows = 11
        num_cols = 5
        freeBlock = 2
        moves = 0
        main_map = HexMap(num_rows, num_cols, tiles, locs)
        while freeBlock:
            bestBlock, score = bot.blockBot(main_map, moves, freeBlock, main_map.pig.pos)
            assert(score == 1), print(f"Score unexpected: {score}")
            print(f"Blocking Position: {bestBlock}")
            pyautogui.click(locs[bestBlock])
            pyautogui.moveTo(100, 800) # Reset position
            main_map.blockTile(bestBlock)
            time.sleep(.3)
            moves += 1
            freeBlock -= 1

        finished = False
        while not finished:
            bestBlock, score = bot.blockBot(main_map, moves, freeBlock, main_map.pig.pos)
            assert(score == 1), print(f"Score unexpected: {score}")
            print(f"Blocking Position: {bestBlock}")
            main_map.blockTile(bestBlock)
            path = main_map.optimalPath(main_map.pig.pos, False)
            print(f"Possible Moves: {path}")
            
            # if bestBlock is none, click some random place to block
            if bestBlock == None: # Either early win or loss
                pyautogui.click(locs[(0, 0)]) # Attempt to click to finish round
                pyautogui.click(locs[(10, 0)])
                break
            pyautogui.click(locs[bestBlock])
            pyautogui.moveTo(100, 800)
            if (path and path[0] == 0): break
            time.sleep(.5)

            if len(path) > 1:
                minx, miny, maxx, maxy, tile_list = pigCaptureHelper(main_map, path)
                movedTile = captureNewPigCV(tile_list, region=(minx, miny, maxx, maxy))
                print(movedTile.CP)
            else:
                movedTile = main_map.tiles[path[0]]
            finished = main_map.movePig(None, movedTile.CP)
            print("\n")
            moves += 1
        pyautogui.moveTo(100, 800) # This move and sleep below is to prevent
        time.sleep(.1)          # "Continue" from being hovered
        hitContinueCV()
        bot.resetSavedStates()
        round += 1

if __name__ == "__main__":
    main()
