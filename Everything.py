import numpy as np
import cv2 as cv
from pupil_apriltags import Detector
import time
import logging
from networktables import NetworkTables
import socket
import sys
import time
import traceback
import Client

def concatenate_images(images, num_rows=3):
    """
    Concatenates a list of images horizontally, and then concatenates the rows vertically.
    Args:
        images (list): A list of images in the form of numpy arrays.
        num_rows (int): The number of rows to concatenate the images in.
    Returns:
        A concatenated image as a numpy array.
    """
    # Check that the list of images is not empty
    if not images:
        return None

    # Determine the number of rows and columns needed
    num_images = len(images)
    num_cols = (num_images + num_rows - 1) // num_rows
    num_rows = min(num_rows, num_images)

    # Create a black canvas to fill up empty spaces
    canvas = np.zeros_like(images[0])

    # Concatenate the images in each row
    rows = []
    for i in range(0, num_rows):
        start = i * num_cols
        end = min((i + 1) * num_cols, num_images)
        row = images[start:end]
        row += [canvas] * (num_cols - len(row))
        row = cv.vconcat(row)
        rows.append(row)

    # Concatenate the rows vertically
    result = cv.hconcat(rows)

    return result



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

frontCap.set(3,640)
frontCap.set(4,480)

palmCap.set(3,640)
palmCap.set(4,480)

apriltagLeftCap.set(3,800)
apriltagLeftCap.set(4,600)
apriltagLeftCap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*'MJPG'))

apriltagRightCap.set(3,800)
apriltagRightCap.set(4,600)
apriltagRightCap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*'MJPG'))

NetworkTables.startClientTeam(2169)
NetworkTables.initialize(server= "10.21.69.2")
imagesToSend = []
while NetworkTables.isConnected():
    print("Connecting to network tables...")
time.sleep(5)
sock = socket.socket()
 # Set those constants for easy access
TCP_IP = '10.21.69.2'

# Grab the port number from the command line
TCP_PORT = int(5800)

    # Connect to the socket with the previous information
print("Connecting to Socket")
try:
    sock.connect((TCP_IP, TCP_PORT))
except:
    print("cannot Connect")
    

    # Enable instant reconnection and disable timeout system
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Spread the good news
print("Connected!")


sd =  NetworkTables.getTable("SmartDashboard")

def apriltag(img, name, fx, fy, cx, cy):

    newValue = False
    det = at_detector.detect(img, estimate_tag_pose=True, camera_params=(fx,fy,cx,cy), tag_size=0.1524)
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
            r31 = pose_r[2][0]
            r32 = pose_r[2][1]
            r33 = pose_r[2][2]
            
            AprilTagYaw = np.round(np.degrees(np.arctan(-r31/np.sqrt((r32 * r32)+(r33 * r33)))),3)
            newValue = True
            sd.putNumber(name + "-apriltag-Yaw", AprilTagYaw)
            sd.putNumber(name + "-apriltag-Z", maxDet.pose_t[1])
            sd.putNumber(name + "-apriltag-Y", maxDet.pose_t[2])
            sd.putNumber(name + "-apriltag-X", maxDet.pose_t[0])
            sd.putNumber(name + "-apriltag-Id", maxDet.tag_id)
            #AprilTagPitch = round(np.degrees(np.arctan(-r32/r33)),3)
            #AprilTagRoll = round(np.degrees(np.arctan(r21/r11)),3)
            imgColor = cv.putText(img, str(maxDet.tag_id), np.array(maxDet.center.tolist(), dtype=np.int64), font, 3, (100, 255, 0), 3, cv.LINE_AA)
    cv.imshow(name, img)
    imagesToSend.append(img)
    if not newValue:
        sd.delete(name + "-apriltag-Yaw")
        sd.delete(name + "-apriltag-X")
        sd.delete(name + "-apriltag-Y")
        sd.delete(name + "-apriltag-Z")
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
    imagesToSend.append(img)
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
                sd.putNumber(camId + name + "-Angle", (np.arctan(vy/vx)* 180) / np.pi)
                img = cv.line(img,(cols-1,righty),(0,lefty),(150,100,40),2)
                
    cv.imshow(name + " " + str(index), img)
    imagesToSend.append(img)
    if not newValue:
        sd.delete(camId + name + "-Center")
        sd.delete(camId + name + "-Angle")

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
    imagesToSend.clear()
    

    try:
        if frontCap.isOpened():
            ret1, imgFront = frontCap.read()


            cone(imgFront, frontIndex, "Front-", False)
            cube(imgFront, frontIndex, "Front-")
            imgFront = cv.cvtColor(imgFront, cv.COLOR_BGR2GRAY)
            imgFront = cv.inRange(imgFront, np.array([120]),np.array([255]))
            apriltag(imgFront, "front", 743.2092175170602,742.142809848907,326.4811764880153,233.65761973429647)
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
            apriltag(imgAprilLeft, "left", 732.65358523156, 734.9632727889218, 366.943605533931, 330.4303688178763)
            sd.putBoolean("Left", True)
        else:
            sd.putBoolean("Left", False)
        if apriltagRightCap.isOpened():
            ret4, imgAprilRight = apriltagRightCap.read()
            imgAprilRight = cv.inRange(imgAprilRight,np.array([100,100,100]),np.array([255,255,255]))
            apriltag(imgAprilRight, "right", 732.65358523156, 734.9632727889218, 366.943605533931, 330.4303688178763)
            sd.putBoolean("Right", True)
        else:
            sd.putBoolean("Right", False)
        Client.runClient(sock, concatenate_images(imagesToSend, 3))
        
    except Exception as e:
        print("stuff got buggy " + str(e))
    

    
    
    
    
    

    if cv.waitKey(1) == ord('q'):
            break
    # When everything done, release the capture
frontCap.release()
palmCap.release()
apriltagLeftCap.release()
apriltagRightCap.release()
cv.destroyAllWindows()

    