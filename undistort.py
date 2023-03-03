
import cv2
import numpy as np
# You should replace these 3 lines with the output in calibration step
DIM=(1920, 1080)
K=np.array([[551.924385771314, 0.0, 937.3847141292987], [0.0, 554.119653561351, 547.4288473267238], [0.0, 0.0, 1.0]])
D=np.array([[-0.10025090596743824], [0.102381740945723], [-0.06909909621098911], [0.014823465749392566]])
def undistort(img):
    h,w = img.shape[:2]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return undistorted_img