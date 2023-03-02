
import cv2
import numpy as np
# You should replace these 3 lines with the output in calibration step
DIM=(1280, 1024)
K=np.array([[530.1645283931713, 0.0, 620.3578631557211], [0.0, 530.7405670208875, 521.3834312880532], [0.0, 0.0, 1.0]])
D=np.array([[-0.05694366761885126], [0.000900714529680055], [-0.0011186853082556065], [-0.00014542058368574722]])
def undistort(img):
    h,w = img.shape[:2]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return undistorted_img