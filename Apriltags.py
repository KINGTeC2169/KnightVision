import logging
import socket
import sys
import time
import traceback

import cv2 as cv
import NetworkTable
import numpy as np
from networktables import NetworkTables
from pupil_apriltags import Detector

at_detector = Detector(
    families="tag16h5",
    nthreads=4,
    quad_decimate=2.0,
    quad_sigma=0.0,
    refine_edges=1,
    decode_sharpening=0.25,
    debug=0
    )

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
            print(maxDet.pose_t[0] * 39 - (maxDet.pose_t[2] * (np.sin((AprilTagYaw * np.pi) / 180 )) * 39))
            #print(maxDet.pose_t[0] * 39)
            if(NetworkTable.isConnected()):
                NetworkTable.sd.putNumber(name + "-apriltag-Yaw", AprilTagYaw)
                #NetworkTable.sd.putNumber(name + "-apriltag-Z", maxDet.pose_t[1]) we dont really care about this
                NetworkTable.sd.putNumber(name + "-apriltag-Y", np.cos((AprilTagYaw * np.pi) / 180) * maxDet.pose_t[2])
                NetworkTable.sd.putNumber(name + "-apriltag-X", maxDet.pose_t[0] - (maxDet.pose_t[2] * (np.sin((AprilTagYaw * np.pi) / 180 ))))
                NetworkTable.sd.putNumberArray(name + "-apriltag-Center", maxDet.center.tolist())
                NetworkTable.sd.putNumber(name + "-apriltag-Id", maxDet.tag_id)
                #AprilTagPitch = round(np.degrees(np.arctan(-r32/r33)),3)
                #AprilTagRoll = round(np.degrees(np.arctan(r21/r11)),3)
    cv.imshow(name, img)
    if not newValue and NetworkTable.isConnected():
        NetworkTable.sd.delete(name + "-apriltag-Yaw")
        NetworkTable.sd.delete(name + "-apriltag-X")
        NetworkTable.sd.delete(name + "-apriltag-Y")
        NetworkTable.sd.delete(name + "-apriltag-Z")
        NetworkTable.sd.delete(name + "-apriltag-Id")
        NetworkTable.sd.delete(name + "-apriltag-Center")