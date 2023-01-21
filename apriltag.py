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
font = cv.FONT_HERSHEY_SIMPLEX

  
# used to record the time at which we processed current frame
new_frame_time = 0

cap = cv.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)
cap.set(cv.CAP_PROP_FPS, 30)
cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*'MJPG'))

def rescale_frame(frame, percent=75):
    width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv.resize(frame, dim, interpolation =cv.INTER_AREA)

while True:
    
    reta,img = cap.read()
    img = rescale_frame(img, 50)
    imgColor = img
    img = cv.GaussianBlur(img,(5,5),0)
    img = cv.inRange(img,np.array([120,120,120]),np.array([255,255,255]))

    det = at_detector.detect(img, estimate_tag_pose=True, camera_params=(1083.1843730953367,1070.1431886531207,586.9131989071315,293.5012883025358), tag_size=0.1524)
    if len(det) > 0:
        maxDet = det[0]
        for i in det:
            if (i.decision_margin > maxDet.decision_margin) and (0 < i.tag_id < 9):
                maxDet = i
        
        imgColor = cv.circle(imgColor, np.array(maxDet.corners.tolist()[0], dtype=np.int64), 10, [98,23,87], 5)
        imgColor = cv.circle(imgColor, np.array(maxDet.corners.tolist()[1], dtype=np.int64), 10, [98,23,87], 5)
        imgColor = cv.circle(imgColor, np.array(maxDet.corners.tolist()[2], dtype=np.int64), 10, [98,23,87], 5)
        imgColor = cv.circle(imgColor, np.array(maxDet.corners.tolist()[3], dtype=np.int64), 10, [98,23,87], 5)
        imgColor = cv.circle(imgColor, np.array(maxDet.center.tolist(), dtype=np.int64), 10, [98,23,87], 5)
        pose_r = maxDet.pose_R
        r11 = [0][0]
        r12 = pose_r[0][1]
        r13 = pose_r[0][2]
        r21 = pose_r[1][0]
        r22 = pose_r[1][1]
        r23 = pose_r[1][2]
        r31 = pose_r[2][0]
        r32 = pose_r[2][1]
        r33 = pose_r[2][2]
        
        AprilTagYaw = np.round(np.degrees(np.arctan(-r31/np.sqrt((r32 * r32)+(r33 * r33)))),3)
        #AprilTagPitch = round(np.degrees(np.arctan(-r32/r33)),3)
        #AprilTagRoll = round(np.degrees(np.arctan(r21/r11)),3)
        imgColor = cv.putText(imgColor, str(maxDet.tag_id), np.array(maxDet.center.tolist(), dtype=np.int64), font, 3, (100, 255, 0), 3, cv.LINE_AA)

    new_frame_time = time.time()
    fps = 1/(new_frame_time-prev_frame_time)
    prev_frame_time = new_frame_time
  
    # converting the fps into integer
    fps = int(fps)
  
    # converting the fps to string so that we can display it on frame
    # by using putText function
    fps = str(fps)
  
    # putting the FPS count on the frame
    cv.putText(imgColor, fps, (7, 70), font, 3, (100, 255, 0), 3, cv.LINE_AA)
    
    cv.imshow("hello", imgColor)
    if cv.waitKey(1) == ord('q'):
        break
# When everything done, release the capture
cap.release()
cv.destroyAllWindows()
