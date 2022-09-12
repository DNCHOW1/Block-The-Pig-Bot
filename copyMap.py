#import mss, pickle, pyautogui, time
import pickle, time, mss, pyautogui
from pyautogui import locateOnScreen, locateCenterOnScreen
from math import sqrt

def distFormula(point1, point2):
    return sqrt((point1.x-point2.x)**2 + (point1.y-point2.y)**2)

def isBlocked(color):
    tol = 40
    mids = (93, 160, 10)
    for i in range(3):
        if abs(mids[i]-color[i]) > tol: return True
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

    '''if locateOnScreen("BlockThePig/pig_right_eye.png", region=(1007, 1118, 1037, 1138), grayscale=True, confidence=0.7):
        # Pig is in default position
        print("Default")
    else:
        # Pig is not in default Position
        print(locateOnScreen("BlockThePig/pig_screenshots/pig_left.png", region=(544, 574, 1340, 1904), grayscale=True, confidence=0.7))
        print(locateOnScreen("BlockThePig/pig_screenshots/pig_right_eye.png", region=(544, 574, 1340, 1904), grayscale=True, confidence=0.7))'''
    tiles[(5, 5)] = "p"
    print(time.perf_counter() - s)
    return tiles, mouse_locs
    with open('BlockThePig/main_realtime_map_data.pkl', 'wb') as output:
        pickle.dump(tiles, output)

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
    for tile in tiles:
        dist = distFormula(loc, tile)
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
