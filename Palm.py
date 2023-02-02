import numpy as np
import cv2 as cv
import time
import logging
from networktables import NetworkTables
import threading
import NetworkTableManager
import multiprocessing


def findObjects(img, name, index):
    contours, heiarchy = cv.findContours(img, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    if len(contours) != 0:
        cnt = max(contours, key = cv.contourArea)
        if cv.contourArea(cnt) > 100:
            rows,cols = img.shape[:2]
            [vx,vy,x,y] = cv.fitLine(cnt, cv.DIST_L2,0,0.01,0.01)

        
            M = cv.moments(cnt)
            try:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                img = cv.circle(img, [cx,cy], 5, [100,90,90], 2)
                NetworkTableManager.sendNetworkTableNumberArray("Palm-" + name + "-Center", [cx,cy])

            except ZeroDivisionError:
                print('balls')

            # I put this here because I was having issuse with the slope being undefined when straight up
            if vx > 0:
                lefty = int((-x*vy/vx) + y)
                righty = int(((cols-x)*vy/vx)+y)
                NetworkTableManager.sendNetworkTableNumber("Palm-" + name + "-Angle", (np.arctan(vy/vx)* 180) / np.pi)
                img = cv.line(img,(cols-1,righty),(0,lefty),(150,100,40),2)
                
    cv.imshow(name + " " + str(index), img)

def palm(index):
    
    
    cap = cv.VideoCapture(index)
    cap.set(3,480)
    cap.set(4,480)



    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    while True:
        # Capture frame-by-frame
        reta, img = cap.read()
        # if frame is read correctly ret is True
        if not reta:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        img = cv.GaussianBlur(img,(5,5),0)
        coneImg = cv.inRange(img,np.array([15,191,90]),np.array([33,255,255]))
        cubeImg = cv.inRange(img,np.array([113,90,110]),np.array([131,255,255]))
        coneThread = threading.Thread(target=findObjects(coneImg, "Cone", index))
        cubeThread = threading.Thread(target=findObjects(cubeImg, "Cube", index))
        #print(NetworkTables.isConnected())
            

        if cv.waitKey(1) == ord('q'):
            break
    # When everything done, release the capture
    cap.release()
    cv.destroyAllWindows()

def Organizer():
    palm(int(input("Gimme a number: ")))


if __name__ == "__main__":
    Organizer()