#!/usr/bin/env python3
# encoding:utf-8
# Data:2021/05/25
# Author:Aiden
# Function: collect calibration image
import os
import cv2
import time
from CalibrationConfig import *

print('Press "space" key to save the image and press "Esc" to exit ')
cap = cv2.VideoCapture(-1)

pictures_list = []
#If calib folder does not exit, create a new one.
if not os.path.exists(save_path):
    os.mkdir(save_path)
else:
    for i in os.listdir(save_path):
        pictures_list.append(i[:-4])

#Calculate the number of the saved pictures
num = 0
while True:
    ret, frame = cap.read()
    if ret:
        Frame = frame.copy()
        cv2.putText(Frame, str(num), (10, 50), cv2.FONT_HERSHEY_COMPLEX, 2.0, (0, 0, 255), 5)
        cv2.imshow("Frame", Frame)
        key = cv2.waitKey(1)
        if key == 27:
            break
        if key == 32:
            while True:
                num += 1
                if num not in pictures_list:
                    #The format of image name: current number of imagess.jpg
                    cv2.imwrite(save_path + str(num) + ".jpg", frame)
                    break
    else:
        time.sleep(0.01)

cap.release()
cv2.destroyAllWindows()
