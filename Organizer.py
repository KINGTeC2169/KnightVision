import multiprocessing 
from multiprocessing import Process
import threading
import Front
import Palm
import apriltag
from networktables import NetworkTables
import cv2 as cv
import NetworkTableManager


NetworkTableManager.getTables()
    
#
Front.Front(0)
Palm.palm(2)
apriltag.aprilTags(4)
apriltag.aprilTags(6)