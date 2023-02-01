import numpy as np
import cv2 as cv
from pupil_apriltags import Detector
import time
import logging
from networktables import NetworkTables
import threading

def findObjects(img, name):
    contours, heiarchy = cv.findContours(img, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    if len(contours) != 0:
        cnt = max(contours, key = cv.contourArea)
        if cv.contourArea(cnt) > 100:
            rows,cols = img.shape[:2]
        
            M = cv.moments(cnt)
            try:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                img = cv.circle(img, [cx,cy], 5, [100,90,90], 2)
                sd.putNumberArray("Front-" + name + "-Center", [cx,cy])

            except ZeroDivisionError:
                print('balls')

                
    cv.imshow(str(controlledby) + " " + name, img)

def main():

    controlledby = int(input("Gimme a number: "))
    time.sleep(5)
    cap = cv.VideoCapture(controlledby)
    cap.set(3,480)
    cap.set(4,480)
    #cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*'MJPG'))


    NetworkTables.startClientTeam(2169)
    NetworkTables.initialize(server= "10.21.69.2")
    at_detector = Detector(
    families="tag16h5",
    nthreads=6,
    quad_decimate=1.0,
    quad_sigma=0.0,
    refine_edges=1,
    decode_sharpening=0.25,
    debug=0
    )

    sd = NetworkTables.getTable("SmartDashboard")
    logging.basicConfig(level=logging.DEBUG)
    lastSlope = 0
    badSlopeCount = 0



    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    while True:
        # Capture frame-by-frame
        reta, img = cap.read()
        # if frame is read correctly ret is True
        if not reta:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        #imgApril = cv.inRange(img ,np.array([100,100,100]),np.array([255,255,255]))
        imgApril = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        

        det = at_detector.detect(imgApril, estimate_tag_pose=True, camera_params=(1083.1843730953367,1070.1431886531207,586.9131989071315,293.5012883025358), tag_size=0.1524)
        if len(det) > 0:
            maxDet = det[0]
            for i in det:
                if (i.decision_margin > maxDet.decision_margin) and (0 < i.tag_id < 9):
                    maxDet = i
            
            imgApril = cv.circle(imgApril, np.array(maxDet.corners.tolist()[0], dtype=np.int64), 10, [98,23,87], 5)
            imgApril = cv.circle(imgApril, np.array(maxDet.corners.tolist()[1], dtype=np.int64), 10, [98,23,87], 5)
            imgApril = cv.circle(imgApril, np.array(maxDet.corners.tolist()[2], dtype=np.int64), 10, [98,23,87], 5)
            imgApril = cv.circle(imgApril, np.array(maxDet.corners.tolist()[3], dtype=np.int64), 10, [98,23,87], 5)
            imgApril = cv.circle(imgApril, np.array(maxDet.center.tolist(), dtype=np.int64), 10, [98,23,87], 5)
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
            cv.imshow("hi", imgApril)

        img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        img = cv.GaussianBlur(img,(5,5),0)
        coneImg = cv.inRange(img,np.array([15,191,90]),np.array([33,255,255]))
        cubeImg = cv.inRange(img,np.array([113,90,110]),np.array([131,255,255]))
        coneThread = threading.Thread(target=findObjects(coneImg, "Cone"))
        cubeThread = threading.Thread(target=findObjects(cubeImg, "Cube"))
        #print(NetworkTables.isConnected())
            

        if cv.waitKey(1) == ord('q'):
            break
    # When everything done, release the capture
    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()