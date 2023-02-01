import time
from pupil_apriltags import Detector
import cv2 as cv
import numpy as np

at_detector = Detector(
   families="tag16h5",
   nthreads=4,
   quad_decimate=1.0,
   quad_sigma=0.0,
   refine_edges=1,
   decode_sharpening=0.25,
   debug=0
)


prev_frame_time = 0
font = cv.FONT_HERSHEY_SIMPLEX

  
# used to record the time at which we processed current frame
new_frame_time = 0

cap = cv.VideoCapture(3)
cap.set(3,1280)
cap.set(4,800)
cap.set(cv.CAP_PROP_FPS, 120)
#cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*'MJPG'))

while True:
    
    reta,img = cap.read()
    
    new_frame_time = time.time()
    fps = 1/(new_frame_time-prev_frame_time)
    prev_frame_time = new_frame_time
  
    # converting the fps into integer
    fps = int(fps)
  
    # converting the fps to string so that we can display it on frame
    # by using putText function
    fps = str(fps)
  
    # putting the FPS count on the frame
    cv.putText(img, fps, (7, 70), font, 3, (100, 255, 0), 3, cv.LINE_AA)
    
    cv.imshow("apriltag", img)
    if cv.waitKey(1) == ord('q'):
        break
# When everything done, release the capture
cap.release()
cv.destroyAllWindows()
