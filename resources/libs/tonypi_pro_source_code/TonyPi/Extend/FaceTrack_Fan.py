#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/TonyPi/')
import cv2
import math
import time
import signal
import threading
import numpy as np
import RPi.GPIO as GPIO
import hiwonder.Misc as Misc
import hiwonder.Board as Board
import hiwonder.Camera as Camera
import hiwonder.ActionGroupControl as AGC
import hiwonder.yaml_handle as yaml_handle

# Fan Tracking

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

# threshold
conf_threshold = 0.6

# model position
modelFile = "/home/pi/TonyPi/models/res10_300x300_ssd_iter_140000_fp16.caffemodel"
configFile = "/home/pi/TonyPi/models/deploy.prototxt"
net = cv2.dnn.readNetFromCaffe(configFile, modelFile)

servo_data = None
def load_config():
    global servo_data
    
    servo_data = yaml_handle.get_yaml_data(yaml_handle.servo_file_path)

load_config()
servo2_pulse = servo_data['servo2']

# Initial position
def initMove():
    Board.setPWMServoPulse(1, 1500, 500)
    Board.setPWMServoPulse(2, servo2_pulse, 500)

d_pulse = 10
move_st = True
start_greet = False
__isRunning = False

# Reset variable
def reset():
    global d_pulse
    global start_greet
    global servo2_pulse    

    d_pulse = 10
    start_greet = False
    servo2_pulse = servo_data['servo2']
    
# Intialization         
def init():
    print("FaceDetect Init")
    reset()
    initMove()

def setFan(start):
    GPIO.setup(24, GPIO.OUT) # corresponds to IO8 of expansion board
    GPIO.setup(26, GPIO.OUT) # corresponds to IO7 of expansion board             
    if start == 1:
        GPIO.output(24, 1)     
        GPIO.output(26, 0)       
    else:
        GPIO.output(24, 0)
        GPIO.output(26, 0)  


def Stop(signum, frame):
    global move_st
    print('closing...')
    move_st = False
    setFan(0) #Turn off fan
    Board.setBusServoPulse(14,425,1000)
    time.sleep(0.8)
    AGC.runActionGroup('stand_slow')

signal.signal(signal.SIGINT, Stop)

start_ = False
def move():
    global start_greet, start_
    global d_pulse, servo2_pulse    
    
    while move_st:
        if __isRunning:
            if start_greet: #Determine whether the face is detected
                start_greet = False
                pulse = int(Misc.map(servo2_pulse, 1000, 2000, 600, 200)) 
                # map the servo on robot's head to the servo on hand
                # drive the servo on hand 
                Board.setBusServoPulse(16,700,1500)  
                time.sleep(1.5)
                Board.setBusServoPulse(14,pulse,1000)
                time.sleep(1)
                setFan(1) #turn on fan
              
            else:
                setFan(0) #turn off fan
                if servo2_pulse > 2000 or servo2_pulse < 1000:
                    d_pulse = -d_pulse
                #left and right rotation, detect
                servo2_pulse += d_pulse       
                Board.setPWMServoPulse(2, servo2_pulse, 50)
                time.sleep(0.05)
        else:
            time.sleep(0.01)
            
# run subthread
th = threading.Thread(target=move)
th.setDaemon(True)
th.start()

size = (320, 240)
def run(img):
    global start_greet
       
    img_copy = img.copy()
    img_h, img_w = img.shape[:2]

    if not __isRunning:
        return img

    blob = cv2.dnn.blobFromImage(img_copy, 1, (150, 150), [104, 117, 123], False, False)
    net.setInput(blob)
    detections = net.forward() #calculate recognition
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold: 
            #Convert the coordniates of recognized face into the coordiate before scaling 
            x1 = int(detections[0, 0, i, 3] * img_w)
            y1 = int(detections[0, 0, i, 4] * img_h)
            x2 = int(detections[0, 0, i, 5] * img_w)
            y2 = int(detections[0, 0, i, 6] * img_h)             
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2, 8) #frame the recgnized face
            if abs((x1 + x2)/2 - img_w/2) < img_w/4:
                start_greet = True
            else:
                setFan(0)
                start_greet = False
    
    return img

if __name__ == '__main__':
    from CameraCalibration.CalibrationConfig import *
    
    #Load parameter 
    param_data = np.load(calibration_param_path + '.npz')

    #obtain parameter
    dim = tuple(param_data['dim_array'])
    k = np.array(param_data['k_array'].tolist())
    d = np.array(param_data['d_array'].tolist())

    print('parameter loading complete')

    #intercept area, 1 represents complete intercept
    scale = 1
    #optimize intrinsic parameters and distortion parameter
    p = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(k, d, dim ,None)
    Knew = p.copy()
    if scale:#change fov
        Knew[(0,1), (0,1)] = scale * Knew[(0,1), (0,1)]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(k, d, np.eye(3), Knew, dim, cv2.CV_16SC2)
  
    init()
    __isRunning = True
    my_camera = Camera.Camera()
    my_camera.camera_open()
    AGC.runActionGroup('stand_slow')
    while move_st:
        img = my_camera.frame
        if img is not None:
            frame = img.copy()
            # correct the camera distortion
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
