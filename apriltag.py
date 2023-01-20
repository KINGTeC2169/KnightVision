import time
from pupil_apriltags import Detector
import cv2 as cv
import numpy as np

at_detector = Detector(
   families="tag16h5",
   nthreads=1,
   quad_decimate=1.0,
   quad_sigma=0.0,
   refine_edges=1,
   decode_sharpening=0.25,
   debug=0
)
prev_frame_time = 0
  
# used to record the time at which we processed current frame
new_frame_time = 0

cap = cv.VideoCapture(1)
cap.set(3,480)
cap.set(4,480)
while True:
    
    reta,img = cap.read()
    imgColor = img
    img = cv.GaussianBlur(img,(5,5),0)
    img = cv.inRange(img,np.array([90,90,90]),np.array([255,255,255]))

    det = at_detector.detect(img)
    if len(det) > 0:
        maxDet = det[0]
        for i in det:
            if i.decision_margin > maxDet.decision_margin:
                maxDet = i
        
        imgColor = cv.circle(imgColor, np.array(maxDet.corners.tolist()[0], dtype=np.int64), 10, [98,23,87], 5)
        imgColor = cv.circle(imgColor, np.array(maxDet.corners.tolist()[1], dtype=np.int64), 10, [98,23,87], 5)
        imgColor = cv.circle(imgColor, np.array(maxDet.corners.tolist()[2], dtype=np.int64), 10, [98,23,87], 5)
        imgColor = cv.circle(imgColor, np.array(maxDet.corners.tolist()[3], dtype=np.int64), 10, [98,23,87], 5)
        imgColor = cv.circle(imgColor, np.array(maxDet.center.tolist(), dtype=np.int64), 10, [98,23,87], 5)
    new_frame_time = time.time()
    fps = 1/(new_frame_time-prev_frame_time)
    prev_frame_time = new_frame_time
  
    # converting the fps into integer
    fps = int(fps)
  
    # converting the fps to string so that we can display it on frame
    # by using putText function
    fps = str(fps)
  
    # putting the FPS count on the frame
    font = cv.FONT_HERSHEY_SIMPLEX
    cv.putText(imgColor, fps, (7, 70), font, 3, (100, 255, 0), 3, cv.LINE_AA)
    cv.imshow("hello", imgColor)
    if cv.waitKey(1) == ord('q'):
        break
# When everything done, release the capture
cap.release()
cv.destroyAllWindows()
