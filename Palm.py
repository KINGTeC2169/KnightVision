import numpy as np
import cv2 as cv
import time
import logging
from networktables import NetworkTables
cap = cv.VideoCapture(0)

NetworkTables.startClientTeam(2169)
NetworkTables.initialize(server= "10.21.69.2")
time.sleep(5)

sd = NetworkTables.getTable("SmartDashboard")
logging.basicConfig(level=logging.DEBUG)
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
    img = cv.inRange(img,np.array([10,90,90]),np.array([43,255,255]))
    contours, heiarchy = cv.findContours(img, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    if len(contours) != 0:
        cnt = max(contours, key = cv.contourArea)
        rows,cols = img.shape[:2]
        [vx,vy,x,y] = cv.fitLine(cnt, cv.DIST_L2,0,0.01,0.01)
        
        # I put this here because I was having issuse with the slope being undefined when straight up
        if vx > 0:
            lefty = int((-x*vy/vx) + y)
            righty = int(((cols-x)*vy/vx)+y)
            sd.putNumber("angle", (np.arctan(vy/vx)* 180) / np.pi)
            img = cv.line(img,(cols-1,righty),(0,lefty),(150,100,40),2)
    cv.imshow("Best Fit", img)
    

    print(NetworkTables.isConnected())
        

    if cv.waitKey(1) == ord('q'):
        break
# When everything done, release the capture
cap.release()
cv.destroyAllWindows()