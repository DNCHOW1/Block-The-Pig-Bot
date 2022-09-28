# Hexagonal Grid
import sys, random, pickle, pyautogui, time
from gameboard import HexMap
from bots import HeuristicBot
from copyMap import captureNewGame, captureNewPig, hitContinue # There should be functions here instead

if __name__ == "__main__":
    time.sleep(2)
    round = 1
    bot = HeuristicBot(3)
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
            print(f"Blocking Position: {bestBlock}")
            pyautogui.click(locs[bestBlock])
            main_map.blockTile(bestBlock)
            time.sleep(.3)
            moves += 1
            freeBlock -= 1

        finished = False
        while not finished:
            bestBlock, score = bot.blockBot(main_map, moves, freeBlock, main_map.pig.pos)
            print(f"Blocking Position: {bestBlock}")
            main_map.blockTile(bestBlock)
            path = main_map.optimalPath(main_map.pig.pos, moves<=2)
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
                tile_list = []
                for p in path:
                    tile_list.append(main_map.tiles[p])
                movedTile = captureNewPig(tile_list)
            else:
                movedTile = main_map.tiles[path[0]]
            finished = main_map.movePig(None, movedTile.CP)
            print("\n")
            moves += 1
        pyautogui.moveTo(100, 800) # This move and sleep below is to prevent
        time.sleep(.1)          # "Continue" from being hovered
        hitContinue()
        bot.resetSavedStates()
        round += 1
        # Possible pig moves should be represented with tiles

    sys.exit()
