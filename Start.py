import logging
import socket
import sys
import time

import Apriltags
import cv2 as cv
import FindCone
import FindCube
import NetworkTable
import numpy as np
from networktables import NetworkTables
from pupil_apriltags import Detector
import SendVideo

frontIndex = 0
palmIndex = 2
apriltagLeftIndex = 4
apriltagRightIndex = 6


# /dev/v4l/by-path use this to get usb so they are perminent

frontCap = cv.VideoCapture()
frontCap.open("/dev/v4l/by-id/usb-Azurewave_Integrated_Camera-video-index0")
palmCap = cv.VideoCapture(palmIndex)
apriltagLeftCap = cv.VideoCapture(apriltagLeftIndex)
apriltagRightCap = cv.VideoCapture(apriltagRightIndex)

frontCap.set(3,640)
frontCap.set(4,480)

palmCap.set(3,640)
palmCap.set(4,480)

apriltagLeftCap.set(3,800)
apriltagLeftCap.set(4,600)
apriltagLeftCap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*'MJPG'))

apriltagRightCap.set(3,800)
apriltagRightCap.set(4,600)
apriltagRightCap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*'MJPG'))

NetworkTable.init()
SendVideo.connect()


while True:
    
    try:
        if frontCap.isOpened():
            ret1, imgFront = frontCap.read()
            if(SendVideo.connected):
                SendVideo.send(imgFront, SendVideo.FrontSock)
            FindCone.cone(imgFront, frontIndex, "Front-", False)
            FindCube.cube(imgFront, frontIndex, "Front-")
            imgFront = cv.cvtColor(imgFront, cv.COLOR_BGR2GRAY)
            imgFront = cv.inRange(imgFront, np.array([120]),np.array([255]))
            Apriltags.apriltag(imgFront, "front", 743.2092175170602,742.142809848907,326.4811764880153,233.65761973429647)
            if(NetworkTable.isConnected()):
                NetworkTable.sd.putBoolean("Front", True)
            
        else:
            if(NetworkTable.isConnected()):
                NetworkTable.sd.putBoolean("Front", False)
        if palmCap.isOpened():
            ret2, imgPalm = palmCap.read()
            if(SendVideo.connected):
                SendVideo.send(imgPalm, SendVideo.PalmSock)
            FindCone.cone(imgPalm, palmIndex, "Palm-", True)
            FindCube.cube(imgPalm, palmIndex, "Palm-")
            if(NetworkTable.isConnected()):
                NetworkTable.sd.putBoolean("Palm", True)
        else:
            if(NetworkTable.isConnected()):
                NetworkTable.sd.putBoolean("Palm", False)
        if apriltagLeftCap.isOpened():
            ret3, imgAprilLeft = apriltagLeftCap.read()
            if(SendVideo.connected):
                SendVideo.send(imgAprilLeft, SendVideo.LeftSock)
            imgAprilLeft = cv.inRange(imgAprilLeft,np.array([100,100,100]),np.array([255,255,255]))
            Apriltags.apriltag(imgAprilLeft, "left", 732.65358523156, 734.9632727889218, 366.943605533931, 330.4303688178763)
            if(NetworkTable.isConnected()):
                NetworkTable.sd.putBoolean("Left", True)
        else:
            if(NetworkTable.isConnected()):
                NetworkTable.sd.putBoolean("Left", False)
        if apriltagRightCap.isOpened():
            ret4, imgAprilRight = apriltagRightCap.read()
            if(SendVideo.connected):
                SendVideo.send(imgAprilRight, SendVideo.RightSock)
            imgAprilRight = cv.inRange(imgAprilRight,np.array([100,100,100]),np.array([255,255,255]))
            Apriltags.apriltag(imgAprilRight, "right", 732.65358523156, 734.9632727889218, 366.943605533931, 330.4303688178763)
            if(NetworkTable.isConnected()):
                NetworkTable.sd.putBoolean("Right", True)
        else:
            if(NetworkTable.isConnected()):
                NetworkTable.sd.putBoolean("Right", False)
        
    except Exception as e:
        print(e)
    

    if cv.waitKey(1) == ord('q'):
            break
    # When everything done, release the capture
frontCap.release()
palmCap.release()
apriltagLeftCap.release()
apriltagRightCap.release()
cv.destroyAllWindows()

    