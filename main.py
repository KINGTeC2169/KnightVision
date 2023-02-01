import time
from pupil_apriltags import Detector
import cv2 as cv
import numpy as np
import threading

at_detector = Detector(
   families="tag25h9",
   nthreads=4,
   quad_decimate=1.0,
   quad_sigma=0.0,
   refine_edges=1,
   decode_sharpening=0.25,
   debug=0
)


def openFeed(index):
    cap = cv.VideoCapture(int(index))
    #cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*'MJPG'))
    while True:
        reta, img = cap.read()
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        #img = cv.inRange(img,np.array([100,100,100]),np.array([255,255,255]))
        

        det = at_detector.detect(img, estimate_tag_pose=True, camera_params=(1083.1843730953367,1070.1431886531207,586.9131989071315,293.5012883025358), tag_size=0.1524)
        if len(det) > 0:
            maxDet = det[0]
            for i in det:
                if (i.decision_margin > maxDet.decision_margin) and (0 < i.tag_id < 9):
                    maxDet = i
            
            img = cv.circle(img, np.array(maxDet.corners.tolist()[0], dtype=np.int64), 10, [98,23,87], 5)
            img = cv.circle(img, np.array(maxDet.corners.tolist()[1], dtype=np.int64), 10, [98,23,87], 5)
            img = cv.circle(img, np.array(maxDet.corners.tolist()[2], dtype=np.int64), 10, [98,23,87], 5)
            img = cv.circle(img, np.array(maxDet.corners.tolist()[3], dtype=np.int64), 10, [98,23,87], 5)
            img = cv.circle(img, np.array(maxDet.center.tolist(), dtype=np.int64), 10, [98,23,87], 5)
        cv.imshow(str(index), img)


        if cv.waitKey(1) == ord('q'):
            break
    # When everything done, release the capture
    cap.release()
    cv.destroyAllWindows()

for i in range(-1, 4):
    cap = cv.VideoCapture(i)
    if(cap.isOpened()):
        threading.Thread(target=openFeed, args=(i, )).start()
        
        
    
        




    
    #reta,img = cap.read()
    #det = at_detector.detect(img, estimate_tag_pose=True, camera_params=(1083.1843730953367,1070.1431886531207,586.9131989071315,293.5012883025358), tag_size=0.1524)
