#!/usr/bin/env python3
import os
import sys
sys.path.append('/home/pi/TonyPi/')
import cv2
import math
import time
import threading
import numpy as np
import RPi.GPIO as GPIO
import hiwonder.Camera as Camera
import hiwonder.Board as Board
import hiwonder.Sonar as Sonar
import hiwonder.apriltag as apriltag
import hiwonder.ActionGroupControl as AGC
import hiwonder.yaml_handle as yaml_handle

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

# Photosensitive control ultrasound RGB




servo_data = yaml_handle.get_yaml_data(yaml_handle.servo_file_path)
# Initial position
def initMove():
    Board.setPWMServoPulse(1, 1500, 500)
    Board.setPWMServoPulse(2, servo_data['servo2'], 500)

def setBuzzer(sleeptime):
    GPIO.setup(31, GPIO.OUT) #set the pin as output mode
    GPIO.output(31, 1)       #set the pin as high level
    time.sleep(sleeptime)   #set latency
    GPIO.output(31, 0)

st = 0
s = Sonar.Sonar()
s.setRGBMode(0)
s.setRGB(1, (0,0,0)) #set to turn off RGB of ultrasonice sensor 
s.setRGB(0, (0,0,0))

def move():
    global st
    
    while True:
        GPIO.setup(26, GPIO.IN) #set the pin as intput mode
        GPIO.setup(24, GPIO.IN)
        state = GPIO.input(24)  #read pin value 
        
        if state:
            time.sleep(0.1)
            if state:
                if st :            #Make a determination to prevent repeated sounding 
                    st = 0
                    setBuzzer(0.1)   #set the buzzer sound for 0.1s 
                    s.setRGB(1, (255,255,255))  #set RGB light as white light
                    s.setRGB(0, (255,255,255))
        else:
            if not st:
                st = 1
                s.setRGB(1, (0,0,0)) #set to turn off RGB
                s.setRGB(0, (0,0,0))
            
        time.sleep(0.01)

# Run subthread
th = threading.Thread(target=move)
th.setDaemon(True)
th.start()

# apriltag detect apriltag
detector = apriltag.Detector(searchpath=apriltag._get_demo_searchpath())

def apriltagDetect(img):   
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    detections = detector.detect(gray, return_image=False)

    if len(detections) != 0:
        for detection in detections:                       
            corners = np.rint(detection.corners)  # get the four corner points 
            cv2.drawContours(img, [np.array(corners, np.int)], -1, (0, 255, 255), 2)

            tag_family = str(detection.tag_family, encoding='utf-8')  # get tag_family
            tag_id = int(detection.tag_id)  # get tag_id

            objective_x, objective_y = int(detection.center[0]), int(detection.center[1])  # center point 
            
            object_angle = int(math.degrees(math.atan2(corners[0][1] - corners[1][1], corners[0][0] - corners[1][0])))  # calculate rotatin angle
            
            return [tag_family, tag_id, objective_x, objective_y]
            
    return None, None, None, None


def run(img):
    
    tag_family, tag_id, objective_x, objective_y = apriltagDetect(img) # apriltag detection
    print('Apriltag:',objective_x,objective_y)
        
    return img

if __name__ == '__main__':
    from CameraCalibration.CalibrationConfig import *
    
    #Load parameter 
    param_data = np.load(calibration_param_path + '.npz')

    #obtain parameter
    dim = tuple(param_data['dim_array'])
    k = np.array(param_data['k_array'].tolist())
    d = np.array(param_data['d_array'].tolist())

    print('加载参数完成 parameter loading complete')

    #intercept area, 1 represents complete intercept
    scale = 1
    #optimize intrinsic parameters and distortion parameter
    p = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(k, d, dim ,None)
    Knew = p.copy()
    if scale:#change fov
        Knew[(0,1), (0,1)] = scale * Knew[(0,1), (0,1)]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(k, d, np.eye(3), Knew, dim, cv2.CV_16SC2)
  
    initMove()
    camera = cv2.VideoCapture(-1)
    
    while True:
        ret,img = camera.read()
        if ret:
            frame = img.copy()
            frame = cv2.remap(frame.copy(), map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
            Frame = run(frame)           
            cv2.imshow('Frame', Frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
        else:
            time.sleep(0.01)
    setFan(0)
    my_camera.camera_close()
    cv2.destroyAllWindows()
    
