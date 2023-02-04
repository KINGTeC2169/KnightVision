import numpy as np
import cv2 as cv
from pupil_apriltags import Detector
import time
import logging
from networktables import NetworkTables


at_detector = Detector(
    families="tag16h5",
    nthreads=4,
    quad_decimate=2.0,
    quad_sigma=0.0,
    refine_edges=1,
    decode_sharpening=0.25,
    debug=0
    )

font = cv.FONT_HERSHEY_SIMPLEX


frontIndex = 0
palmIndex = 2
apriltagLeftIndex = 4
apriltagRightIndex = 6



frontCap = cv.VideoCapture(frontIndex)
palmCap = cv.VideoCapture(palmIndex)
apriltagLeftCap = cv.VideoCapture(apriltagLeftIndex)
apriltagRightCap = cv.VideoCapture(apriltagRightIndex)

frontCap.set(3,480)
frontCap.set(4,480)

palmCap.set(3,480)
palmCap.set(4,480)

apriltagLeftCap.set(3,800)
apriltagLeftCap.set(4,600)
apriltagLeftCap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*'MJPG'))

apriltagRightCap.set(3,800)
apriltagRightCap.set(4,600)
apriltagRightCap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*'MJPG'))

NetworkTables.startClientTeam(2169)
NetworkTables.initialize(server= "10.21.69.2")
while not NetworkTables.isConnected():
    print("Connecting to network tables...")
time.sleep(5)


sd =  NetworkTables.getTable("SmartDashboard")

def apriltag(img, name):
    
    newValue = False
    det = at_detector.detect(img, estimate_tag_pose=True, camera_params=(1083.1843730953367,1070.1431886531207,586.9131989071315,293.5012883025358), tag_size=0.1524)
    if len(det) > 0:
        maxDet = det[0]
        for i in det:
            if (i.decision_margin > maxDet.decision_margin):
                maxDet = i
        if(0 < i.tag_id < 9):
            img = cv.circle(img, np.array(maxDet.corners.tolist()[0], dtype=np.int64), 10, [98,23,87], 5)
            img = cv.circle(img, np.array(maxDet.corners.tolist()[1], dtype=np.int64), 10, [98,23,87], 5)
            img = cv.circle(img, np.array(maxDet.corners.tolist()[2], dtype=np.int64), 10, [98,23,87], 5)
            img = cv.circle(img, np.array(maxDet.corners.tolist()[3], dtype=np.int64), 10, [98,23,87], 5)
            img = cv.circle(img, np.array(maxDet.center.tolist(), dtype=np.int64), 10, [98,23,87], 5)
            pose_r = maxDet.pose_R
            pose_t = maxDet.pose_t[2] * 39.3701
            r31 = pose_r[2][0]
            r32 = pose_r[2][1]
            r33 = pose_r[2][2]
            
            AprilTagYaw = np.round(np.degrees(np.arctan(-r31/np.sqrt((r32 * r32)+(r33 * r33)))),3)
            newValue = True
            sd.putNumber(name + "-apriltag-Yaw", AprilTagYaw)
            sd.putNumber(name + "-apriltag-X", pose_t)
            sd.putNumber(name + "-apriltag-Id", maxDet.tag_id)
            #AprilTagPitch = round(np.degrees(np.arctan(-r32/r33)),3)
            #AprilTagRoll = round(np.degrees(np.arctan(r21/r11)),3)
            imgColor = cv.putText(img, str(maxDet.tag_id), np.array(maxDet.center.tolist(), dtype=np.int64), font, 3, (100, 255, 0), 3, cv.LINE_AA)
    cv.imshow(name, img)
    if not newValue:
        sd.delete(name + "-apriltag-Yaw")
        sd.delete(name + "-apriltag-X")
        sd.delete(name + "-apriltag-Id")


def findObjects(img, name, index, camId):
    newValue = False
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
                newValue = True
                sd.putNumberArray(camId + name + "-Center", [cx,cy])

            except ZeroDivisionError:
                print('balls')

    cv.imshow(name + " " + str(index), img)
    if not newValue:
        sd.delete(camId + name + "-Center")
        

def findObjWithLines(img, name, index, camId):
    newValue = False
    contours, heiarchy = cv.findContours(img, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    if len(contours) != 0:
        cnt = max(contours, key = cv.contourArea)
        if cv.contourArea(cnt) > 100:
            rows,cols = img.shape[:2]
            [vx,vy,x,y] = cv.fitLine(cnt, cv.DIST_L2,0,0.01,0.01)
        
            M = cv.moments(cnt)
            try:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                img = cv.circle(img, [cx,cy], 5, [100,90,90], 2)
                newValue = True
                sd.putNumberArray(camId + name + "-Center", [cx,cy])

            except ZeroDivisionError:
                print('balls')

            if vx > 0:
                lefty = int((-x*vy/vx) + y)
                righty = int(((cols-x)*vy/vx)+y)
                sd.putNumber("Palm-" + name + "-Angle", (np.arctan(vy/vx)* 180) / np.pi)
                img = cv.line(img,(cols-1,righty),(0,lefty),(150,100,40),2)
                
    cv.imshow(name + " " + str(index), img)
    if not newValue:
        sd.delete(camId + name + "-Center")
        sd.delete("Palm-" + name + "-Angle")

def cube(img, index, camId):
    img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    img = cv.GaussianBlur(img,(5,5),0)
    #coneImg = cv.inRange(img,np.array([15,191,90]),np.array([33,255,255]))
    cubeImg = cv.inRange(img,np.array([113,90,110]),np.array([131,255,255]))
    findObjects(cubeImg, "Cube", index, camId)

def cone(img, index, camId, hasLines):
    img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    img = cv.GaussianBlur(img,(5,5),0)
    coneImg = cv.inRange(img,np.array([15,191,90]),np.array([33,255,255]))
    #cubeImg = cv.inRange(img,np.array([113,90,110]),np.array([131,255,255]))
    if hasLines:
        findObjWithLines(coneImg, "Cone", index, camId)
    else:
        findObjects(coneImg, "Cone", index, camId)



while True:
    if frontCap.isOpened():
        ret1, imgFront = frontCap.read()
        cone(imgFront, frontIndex, "Front-", False)
        cube(imgFront, frontIndex, "Front-")
        imgFront = cv.cvtColor(imgFront, cv.COLOR_BGR2GRAY)
        imgFront = cv.inRange(imgFront, np.array([120]),np.array([255]))
        apriltag(imgFront, "front")
        sd.putBoolean("Front", True)
    else:
        sd.putBoolean("Front", False)
    if palmCap.isOpened():
        ret2, imgPalm = palmCap.read()
        cone(imgPalm, palmIndex, "Palm-", True)
        cube(imgPalm, palmIndex, "Palm-")
        sd.putBoolean("Palm", True)
    else:
        sd.putBoolean("Palm", False)
    if apriltagLeftCap.isOpened():
        ret3, imgAprilLeft = apriltagLeftCap.read()
        imgAprilLeft = cv.inRange(imgAprilLeft,np.array([100,100,100]),np.array([255,255,255]))
        apriltag(imgAprilLeft, "left")
        sd.putBoolean("Left", True)
    else:
        sd.putBoolean("Left", False)
    if apriltagRightCap.isOpened():
        ret4, imgAprilRight = apriltagRightCap.read()
        imgAprilRight = cv.inRange(imgAprilRight,np.array([100,100,100]),np.array([255,255,255]))
        apriltag(imgAprilRight, "right")
        sd.putBoolean("Right", True)
    else:
        sd.putBoolean("Right", False)

    
    
    
    
    

    if cv.waitKey(1) == ord('q'):
            break
    # When everything done, release the capture
frontCap.release()
palmCap.release()
apriltagLeftCap.release()
apriltagRightCap.release()
cv.destroyAllWindows()

    