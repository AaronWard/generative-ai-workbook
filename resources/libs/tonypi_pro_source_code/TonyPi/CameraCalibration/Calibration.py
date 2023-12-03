#!/usr/bin/env python3
# encoding:utf-8
import os
import cv2
import glob
import numpy as np
from CalibrationConfig import *

#mono camera calibration

def get_K_D(checkerboard_size, imgsPath, param_save_path):
    #Parameter 1: The horizontal and vertical interior corners of the checkboard
    #Parameter 2: The path of image to be calibrated
    #Parameter 3: the storage path of parameter file after calibration

    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC+cv2.fisheye.CALIB_CHECK_COND+cv2.fisheye.CALIB_FIX_SKEW

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((1, checkerboard_size[1]*checkerboard_size[0], 3), np.float32)
    objp[0,:,:2] = np.mgrid[0:checkerboard_size[0],0:checkerboard_size[1]].T.reshape(-1,2)

    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    #calibration collection image storage path
    images = glob.glob(imgsPath + '*.jpg')
    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (checkerboard_size[0], checkerboard_size[1]), cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)

            corners2 = cv2.cornerSubPix(gray, corners, (3, 3), (-1, -1), criteria)
            imgpoints.append(corners2)
            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, (checkerboard_size[0], checkerboard_size[1]), corners2, ret)
        else:
            print('Not find object points will be delect:', fname)
            os.system('sudo rm ' + fname)
    while True:
        N_OK = len(objpoints)
        K = np.zeros((3, 3))
        D = np.zeros((4, 1))
        rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
        tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
        try:
            rms, _, _, _, _ = cv2.fisheye.calibrate(
                objpoints,
                imgpoints,
                gray.shape[::-1],
                K,
                D,
                rvecs,
                tvecs,
                calibration_flags,
                criteria
            )
            break
        except cv2.error as err:
            idx = int(str(err).split('array ')[1][0])  # Parse index of invalid image from error message
            print('invalid image will be delect', images[idx])
            os.system('sudo rm ' + images[idx])
            del objpoints[idx]
            del imgpoints[idx]
            del images[idx]
            
    DIM = gray.shape[::-1]
    print("\nFound " + str(N_OK) + " valid images for calibration")
    print("resolution\t: DIM=" + str(gray.shape[::-1]))
    print("intrinsic\t: K=np.array(" + str(K.tolist()) + ")")
    print("Distortion coefficients: D=np.array(" + str(D.tolist()) + ")")
    
    #save parameter
    np.savez(param_save_path, dim_array = DIM, k_array = K, d_array = D, fmt="%d", delimiter=" ")    
    print('param save successful\n')  

    return DIM, K, D

if __name__ == '__main__':
    print('********start calibrating***********')
    get_K_D(calibration_size, save_path, calibration_param_path)
    print('********calibration complete***********')
