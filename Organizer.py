from multiprocessing import Process
import Front
import Palm
import apriltag
from networktables import NetworkTables
import cv2 as cv
import NetworkTableManager


NetworkTableManager.getTables()
NetworkTableManager.sendNetworkTableNumber("balls", 54.7)
    
Process(target=Front.Front, args=(0, )).start()
Process(target=Palm.palm, args=(2, )).start()
Process(target=apriltag.aprilTags, args=(4, )).start()
Process(target=apriltag.aprilTags, args=(6, )).start()
