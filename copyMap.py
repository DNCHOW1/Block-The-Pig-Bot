#import mss, pickle, pyautogui, time
import pickle, time, mss, pyautogui
from pyautogui import locateOnScreen, locateCenterOnScreen
from math import sqrt

import cv2 as cv
import numpy as np
from PIL import ImageGrab
from gameboard import Tile

PIG_REGION = (600, 580, 1350, 1800)
CONTINUE_REGION = (670, 1470, 1180, 1621)
CONTINUE_BUTTON = cv.imread('./pig_screenshots/continue_button.png')
# PIG_LEFT = cv.imread('./pig_screenshots/pig_left.png')
# PIG_RIGHT = cv.imread('./pig_screenshots/pig_right.png')
PIG_SKIN = cv.imread('./pig_screenshots/pig_skin.PNG')

# img = ImageGrab.grab(bbox=PIG_REGION)
# img_cv = cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)
# match_prob = cv.matchTemplate(img_cv, PIG_SKIN, cv.TM_CCOEFF_NORMED)
# dy, dx = np.unravel_index(match_prob.argmax(), match_prob.shape)

def distFormula(point1, point2):
    return sqrt(sum((a-b)**2 for a,b in zip(point1, point2)))
    # return sqrt((point1.x-point2.x)**2 + (point1.y-point2.y)**2)

def isBlocked(color, tolerance=40):
    mids = (93, 160, 10) # What normal grass block rgb values typically avg around
    for i in range(3):
        if abs(mids[i]-color[i]) > tolerance: return True
    return False

def captureNewGame():
    origX, origY = 546, 549 # 549
    sX, sY = 177, 136 # 135
    tiles = {}
    mouse_locs = {}

    s = time.perf_counter()
    with mss.mss() as sct:
        region = {'top': origX, 'left': origY, 'width': 950, 'height': 1480}
        img = sct.grab(region)
        for i in range(11):
            cond = (i%2)
            for j in range(cond, 10, 2):
                pointX, pointY = sX*j//2, i*sY
                coord = (origX + sX*j//2, origY + i*sY)
                # pyautogui.moveTo(coord)
                # time.sleep(.5)
                if i==8 and j==4: # Edge case where the text bounces onto cursor
                    pointX, pointY = 975-origX, 1637-origY
                    coord = (pointX+origX, pointY+origY)
                rgb = img.pixel(pointX, pointY)
                # time.sleep(.2)
                # print(f"Row {i} Col {j}: {rgb}")
                b = isBlocked(rgb)
                '''if i == 8:
                    pyautogui.moveTo(coord)
                    time.sleep(1)
                    print(rgb, b)'''


                tiles[(i, j)] = b and (i!=5 or j//2!=2)
                mouse_locs[(i, j)] = (coord[0], coord[1])
                #if i == 8: time.sleep(.5)
                #time.sleep(.5)

    tiles[(5, 5)] = "p"
    print(time.perf_counter() - s)
    return tiles, mouse_locs
    # with open('BlockThePig/main_realtime_map_data.pkl', 'wb') as output:
    #     pickle.dump(tiles, output)

def captureNewPigCV(tiles, region=PIG_REGION):
    x, y = PIG_SKIN.shape[:2]
    with mss.mss() as sct:
        region = {'top': region[0], 'left': region[1], 'width': region[2]-region[0], 'height': region[3]-region[1]}
        img = sct.grab(region)
    img_cv = cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)
    match_prob = cv.matchTemplate(img_cv, PIG_SKIN, cv.TM_CCOEFF)
    match_location = np.unravel_index(match_prob.argmax(), match_prob.shape)
    assert(match_location) # Make sure pig is found

    dy, dx = match_location # Amount to offset
    lowest = 10000
    candidate = None
    true_tile = (x//2 + dx + region[0], y//2 + dy + region[1])
    for tile in tiles:
        dist = distFormula(true_tile, tile.getPixelCoord())
        print(dist)
        if dist < lowest:
            candidate = tile
            lowest = dist
    print(lowest)
    return candidate

def hitContinueCV():
    img = ImageGrab.grab(bbox=CONTINUE_REGION)
    img_cv = cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)
    match_prob = cv.matchTemplate(img_cv, CONTINUE_BUTTON, cv.TM_CCOEFF_NORMED)
    match_location = np.unravel_index(match_prob.argmax(), match_prob.shape)
    assert(match_location) # Make sure "Continue" is found

    # for x, y in zip(*match_locations[::-1]): cv.rectangle(img_cv, (x, y), (x+width, y+height), (0,0,255), 1)

    time.sleep(.2)
    pyautogui.click((932, 1570)) # Center Location of Continue Button
    print("Waiting for next round", end="")
    for i in range(3):
        print(".", end="")
        time.sleep(1.25)
    print()

def captureNewPig(tiles, debug = False): # Needs to get the new pig position
    region = (550, 525, 910, 1421)
    loc = locateCenterOnScreen("./pig_screenshots/pig_left.png", region=region, grayscale=True, confidence=.7)
    print(loc)
    if not loc:
        loc = locateCenterOnScreen("./pig_screenshots/pig_right.png", region=region, grayscale=True, confidence=.7)
    lowest = 10000
    candidate = None
    if debug:
        print(loc)
        pyautogui.moveTo(loc)
        region = (670, 1470, 510, 151)
        # pyautogui.moveTo(region[0], region[1])
        pyautogui.moveTo(region[0]+region[2], region[1]+region[3])
        return
    assert(loc) # Assert that pig actually found

    true_loc = (loc.x, loc.y)
    for tile in tiles:
        dist = distFormula(true_loc, tile.getPixelCoord())
        if dist < lowest:
            candidate = tile
            lowest = dist
    print(lowest)
    return candidate

def hitContinue():
    region = (670, 1470, 510, 151)
    loc = locateCenterOnScreen("./pig_screenshots/continue_button.png", region=region, grayscale=True, confidence=.9)
    assert(loc)
    print("Clicking Continue.")
    time.sleep(.2)
    pyautogui.click(loc)
    print("Waiting for next round", end="")
    for i in range(3):
        print(".", end="")
        time.sleep(1.25)
    print()

if __name__ == "__main__":
    captureNewPig(None, debug=True)
    # captureNewGame()
