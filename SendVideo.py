import logging
import socket
import sys
import time
import traceback

import Apriltags
import cv2 as cv
import FindCone
import FindCube
import NetworkTable
import numpy as np
from networktables import NetworkTables
from pupil_apriltags import Detector



def connect():
    global FrontSock
    global LeftSock
    global RightSock
    global PalmSock
    global connected
    FrontSock = socket.socket()
    LeftSock = socket.socket()
    RightSock = socket.socket()
    PalmSock = socket.socket()
    # Set those constants for easy access
    #10.21.69.2
    TCP_IP = '10.21.69.2'

        # Connect to the socket with the previous information
    print("Connecting to Socket")
    try:
        FrontSock.connect((TCP_IP, 5800))
        LeftSock.connect((TCP_IP, 5801))
        RightSock.connect((TCP_IP, 5802))
        PalmSock.connect((TCP_IP, 5803))
        connected = True
    except:
        print("Cannot connect")
        connected = False

        

        # Enable instant reconnection and disable timeout system
    FrontSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    LeftSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    RightSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    PalmSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Spread the good news
    print("Connected to Sockets")

def send(img, sock):
    # Grab a frame from the webcam
    frame = img

    # C R O N C H   that image down to half size
    newX, newY = frame.shape[1] * .5, frame.shape[0] * .5
    frame = cv.resize(frame, (int(newX), int(newY)))

    # C R O N C H   that image down to extremely compressed JPEG
    encode_param = [int(cv.IMWRITE_JPEG_QUALITY), 7]
    result, imgencode = cv.imencode('.jpg', frame, encode_param)

    # Encode that JPEG string into a NumPy array for compatibility on the other side
    data = np.array(imgencode)

    # Turn NumPy array into a string so we can ship er' on over the information superhighway
    stringData = data.tostring()

    # Send the size of the data for efficient unpacking
    sock.send(str(len(stringData)).ljust(16).encode())

    # Might as well send the actual data while we're sending things
    sock.send(stringData)

