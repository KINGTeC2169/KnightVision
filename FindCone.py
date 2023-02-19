import logging
import socket
import sys
import time
import traceback

import cv2 as cv
import FindObj
import FindObjWithSlopes
import NetworkTable
import numpy as np
from networktables import NetworkTables
from pupil_apriltags import Detector


def cone(img, index, camId, hasLines):
    img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    img = cv.GaussianBlur(img,(5,5),0)
    coneImg = cv.inRange(img,np.array([15,191,90]),np.array([33,255,255]))
    #cubeImg = cv.inRange(img,np.array([113,90,110]),np.array([131,255,255]))
    if hasLines:
        FindObjWithSlopes.findObjWithLines(coneImg, "Cone", index, camId)
    else:
        FindObj.findObjects(coneImg, "Cone", index, camId)