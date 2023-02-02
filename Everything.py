import numpy as np
import cv2 as cv
from pupil_apriltags import Detector
import time
import logging
from networktables import NetworkTables


at_detector = Detector(
    families="tag16h5",
    nthreads=4,
    quad_decimate=1.0,
    quad_sigma=0.0,
    refine_edges=1,
    decode_sharpening=0.25,
    debug=0
    )

font = cv.FONT_HERSHEY_SIMPLEX


frontIndex = 4
palmIndex = 2
apriltagLeftIndex = 0
apriltagRightIndex = 6



frontCap = cv.VideoCapture(frontIndex)
palmCap = cv.VideoCapture(palmIndex)
apriltagLeftCap = cv.VideoCapture(apriltagLeftIndex)
apriltagRightCap = cv.VideoCapture(apriltagRightIndex)

frontCap.set(3,480)
frontCap.set(4,480)

palmCap.set(3,480)
palmCap.set(4,480)

apriltagLeftCap.set(3,1280)
apriltagLeftCap.set(4,800)
apriltagLeftCap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*'MJPG'))

apriltagRightCap.set(3,1280)
apriltagRightCap.set(4,800)
apriltagRightCap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*'MJPG'))

NetworkTables.startClientTeam(2169)
NetworkTables.initialize(server= "10.21.69.2")
while not NetworkTables.isConnected():
    print("Connecting to network tables...")
time.sleep(5)


sd =  NetworkTables.getTable("SmartDashboard")

def apriltag(img, name):
    img = cv.inRange(img,np.array([100,100,100]),np.array([255,255,255]))

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
        imgColor = cv.putText(img, str(maxDet.tag_id), np.array(maxDet.center.tolist(), dtype=np.int64), font, 3, (100, 255, 0), 3, cv.LINE_AA)
    cv.imshow(name, img)


def findObjects(img, name, index, camId):
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
                sd.putNumberArray(camId + name + "-Center", [cx,cy])

            except ZeroDivisionError:
                print('balls')

    cv.imshow(name + " " + str(index), img)

def cube(img, index, camId):
    img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    img = cv.GaussianBlur(img,(5,5),0)
    #coneImg = cv.inRange(img,np.array([15,191,90]),np.array([33,255,255]))
    cubeImg = cv.inRange(img,np.array([113,90,110]),np.array([131,255,255]))
    findObjects(cubeImg, "Cube", index, camId)

def cone(img, index, camId):
    img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    img = cv.GaussianBlur(img,(5,5),0)
    #coneImg = cv.inRange(img,np.array([15,191,90]),np.array([33,255,255]))
    cubeImg = cv.inRange(img,np.array([113,90,110]),np.array([131,255,255]))
    findObjects(cubeImg, "Cone", index, camId)



while True:
    ret1, imgFront = frontCap.read()
    ret2, imgPalm = palmCap.read()
    ret3, imgAprilLeft = apriltagLeftCap.read()
    ret4, imgAprilRight = apriltagRightCap.read()

    apriltag(imgAprilLeft, "left")
    apriltag(imgAprilRight, "right")
    #cv.imshow("balls", imgAprilRight)
    cone(imgFront, frontIndex, "Front-")
    cube(imgFront, frontIndex, "Front-")
    cone(imgPalm, palmIndex, "Palm-")
    cube(imgPalm, palmIndex, "Palm-")

    if cv.waitKey(1) == ord('q'):
            break
    # When everything done, release the capture
frontCap.release()
palmCap.release()
apriltagLeftCap.release()
apriltagRightCap.release()
cv.destroyAllWindows()

    