import logging
import socket
import sys
import time
import traceback

import cv2 as cv
import numpy as np
from networktables import NetworkTables
from pupil_apriltags import Detector



def init():
    global sd
    NetworkTables.startClientTeam(2169)
    NetworkTables.initialize(server= "10.21.69.2")
    while NetworkTables.isConnected():
        print("Connecting to network tables...")
    sd = NetworkTables.getTable("SmartDashboard")

    
def isConnected():
    return NetworkTables.isConnected()
