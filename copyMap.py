#import mss, pickle, pyautogui, time
import pickle, time, mss, pyautogui
from pyautogui import locateOnScreen

def isBlocked(color):
    tol = 40
    mids = (93, 160, 10)
    for i in range(3):
        if abs(mids[i]-color[i]) > tol: return True
    return False

origX, origY = 546, 574
sX, sY = 177, 133
tiles = {}

with mss.mss() as sct:
    region = {'top': origX, 'left': origY, 'width': 1340, 'height': 1904}
    img = sct.grab(region)
    for i in range(11):
        cond = (i%2)
        for j in range(cond, 10, 2):
            pointX, pointY = sX*j//2, i*sY
            coord = (origX + sX*j//2, origY + i*sY)
            if i==8 and j==4: # Edge case where the text bounces onto cursor
                pointX, pointY = 975-origX, 1637-origY
                coord = (pointX+origX, pointY+origY)

            rgb = img.pixel(pointX, pointY)
            b = isBlocked(rgb)
            '''if i == 8:
                pyautogui.moveTo(coord)
                time.sleep(1)
                print(rgb, b)'''


            tiles[(i, j)] = b and (i!=5 or j//2!=2)
            #if i == 8: time.sleep(.5)
            #time.sleep(.5)

if locateOnScreen("BlockThePig/pig_right.png", region=(991, 1107, 1038, 1226), grayscale=True, confidence=0.7):
    # Pig is in default position
    print("Default")
else:
    # Pig is not in default Position
    print(locateOnScreen("BlockThePig/pig_left.png", region=(544, 574, 1340, 1904), grayscale=True, confidence=0.7))
    print(locateOnScreen("BlockThePig/pig_right.png", region=(544, 574, 1340, 1904), grayscale=True, confidence=0.7))
tiles[(5, 5)] = "p" # Temporary Fix
add = False
if __name__ == "__main__":
    if add:
        with open('BlockThePig/multiple_map_data.pkl', 'ab') as output:
            pickle.dump(tiles, output)
else:
    with open('BlockThePig/realtime_map_data.pkl', 'wb') as output:
        pickle.dump(tiles, output)
