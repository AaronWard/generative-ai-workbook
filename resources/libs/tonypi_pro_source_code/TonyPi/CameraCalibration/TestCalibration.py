#!/usr/bin/env python3
# encoding:utf-8
import cv2
import time
import numpy as np
from CalibrationConfig import *

print('Test distortion calibration, press "Ecs" to exit')

#Load parameter
param_data = np.load(calibration_param_path + '.npz')

#Get parameter 
dim = tuple(param_data['dim_array'])
k = np.array(param_data['k_array'].tolist())
d = np.array(param_data['d_array'].tolist())

print('loading parameter complete')
print('dim:\n', dim)
print('k:\n', k)
print('d:\n', d)

#intercept area, 1 represents complete intercept
scale = 1
#optimize intrinsic parameters and distortion parameter
p = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(k, d, dim ,None)
Knew = p.copy()
if scale:#change fov
    Knew[(0,1), (0,1)] = scale * Knew[(0,1), (0,1)]
map1, map2 = cv2.fisheye.initUndistortRectifyMap(k, d, np.eye(3), Knew, dim, cv2.CV_16SC2)

cap = cv2.VideoCapture(-1)
while True:
    t1 = cv2.getTickCount()
    ret, Frame = cap.read()
    if ret:
        frame = Frame.copy()
        dst = cv2.remap(frame.copy(), map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        t2 = cv2.getTickCount()
        time_r = (t2 - t1) / cv2.getTickFrequency()               
        fps = 1.0/time_r

        cv2.putText(frame, "{}x{}".format(dim[0], dim[1]),
                    (10, frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 0, 0), 2)
        cv2.putText(frame, "FPS:{}".format(int(fps)),
                    (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 0, 0), 2)
        cv2.imshow('origin', frame)
        cv2.imshow('redress',dst)
        key = cv2.waitKey(1)
        if key == 27:
            break
    else:
        time.sleep(0.01)
cap.release()
cv2.destroyAllWindows()
