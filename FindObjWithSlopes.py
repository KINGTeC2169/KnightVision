import logging
import socket
import sys
import time
import traceback

import cv2 as cv
import NetworkTable
import numpy as np
from networktables import NetworkTables
from pupil_apriltags import Detector


def findObjWithLines(img, name, index, camId):
    newValue = False
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
                newValue = True
                if(NetworkTable.isConnected()):
                    NetworkTable.sd.putNumberArray(camId + name + "-Center", [cx,cy])

            except ZeroDivisionError:
                print('balls')

            if vx > 0:
                lefty = int((-x*vy/vx) + y)
                righty = int(((cols-x)*vy/vx)+y)
                if(NetworkTable.isConnected()):
                    NetworkTable.sd.putNumber(camId + name + "-Angle", (np.arctan(vy/vx)* 180) / np.pi)
                img = cv.line(img,(cols-1,righty),(0,lefty),(150,100,40),2)
                
    cv.imshow(name + " " + str(index), img)
    if not newValue and NetworkTable.isConnected():
        NetworkTable.sd.delete(camId + name + "-Center")
        NetworkTable.sd.delete(camId + name + "-Angle")