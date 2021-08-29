#import mss, pickle, pyautogui, time
import pickle, mss, time, pyautogui

def isBlocked(color):
    tol = 40
    mids = [93, 160, 10]
    for i in range(3):
        if abs(mids[i]-color[i]) > tol: return True
    return False

origX, origY = 544, 574
sX, sY = 177, 133
tiles = {}

with mss.mss() as sct:
    for i in range(11):
        cond = (i%2)
        for j in range(cond, 10, 2):
            coord = (origX + sX*j//2, origY + i*sY)
            region = {'top': coord[1], 'left': coord[0], 'width': 1, 'height': 1}
            #print(coord)
            #pyautogui.moveTo(coord)

            img = sct.grab(region)
            rgb = img.pixel(0, 0)

            b = isBlocked(rgb)
            #if (i, j) == (4, 4): print(rgb, b)
            #print(b or i==5 and j//2==2)

            tiles[(i, j)] = b and (i!=5 or j//2!=2)
            #time.sleep(1)
tiles[(5, 5)] = "p" # Temporary Fix
add = False
if __name__ == "__main__":
    with open('BlockThePig/multiple_map_data.pkl', 'ab') as output:
        pickle.dump(tiles, output)
else:
    with open('BlockThePig/map_data5.pkl', 'wb') as output:
        pickle.dump(tiles, output)
