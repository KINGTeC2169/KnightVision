from multiprocessing import Process
import time
from pupil_apriltags import Detector
import cv2 as cv
import numpy as np
import threading
import Front
import Palm
import apriltag


Process(target=Front.Front, args=(0, )).start()
Process(target=Palm.palm, args=(2, )).start()
Process(target=apriltag.aprilTags, args=(4, )).start()
Process(target=apriltag.aprilTags, args=(6, )).start()