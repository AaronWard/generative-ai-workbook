#!/usr/bin/python3
# coding=utf8
import os
import sys
import cv2
import time
import math
import threading
import numpy as np
sys.path.append('/home/pi/TonyPi/')
import hiwonder.Misc as Misc
import hiwonder.Board as Board
import hiwonder.PID as PID
import hiwonder.ActionGroupControl as AGC
import hiwonder.yaml_handle as yaml_handle

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

# step

go_forward = 'go_forward'
go_forward_one_step = 'go_forward_one_step'
turn_right = 'turn_right_small_step_a'
turn_left  = 'turn_left_small_step_a'        
left_move = 'left_move_20'
right_move = 'right_move_20'
go_turn_right = 'turn_right'
go_turn_left = 'turn_left'

lab_data = None
servo_data = None

def load_config():
    global lab_data, servo_data
    
    lab_data = yaml_handle.get_yaml_data(yaml_handle.lab_file_path)
    servo_data = yaml_handle.get_yaml_data(yaml_handle.servo_file_path)

load_config()

# Initial position
def initMove():
    Board.setPWMServoPulse(1, 1000, 500)
    Board.setPWMServoPulse(2,servo_data['servo2'],500)   

object_left_x, object_right_x, object_center_y, object_angle = -2, -2, -2, 0
switch = False
# Reset variable
def reset():
    global object_left_x, object_right_x
    global object_center_y, object_angle, switch
    
    object_left_x, object_right_x, object_center_y, object_angle = -2, -2, -2, 0
    
def init():
    load_config()
    initMove()
    reset()

def setBuzzer(sleep):
    Board.setBuzzer(1) # Turn on 
    time.sleep(sleep) # Delay
    Board.setBuzzer(0) #Turn off 

# Find out the contour with the maximum area
# The parameter is the list of the contour to be compared
def getAreaMaxContour(contours, area_min=10):
    contour_area_temp = 0
    contour_area_max = 0
    area_max_contour = None

    for c in contours:  # loop all the contours
        contour_area_temp = math.fabs(cv2.contourArea(c))  # Calculate the contour area
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp >= area_min: 
            # Only when the area is greater than the set value, the maximum contour is effective in order to avoid interference.
                area_max_contour = c

    return area_max_contour, contour_area_max  # Return the maximum contour

size = (640, 480)
# Colored positioning vision processing function
def color_identify(img, img_draw, target_color = 'blue'):
    
    img_w = img.shape[:2][1]
    img_h = img.shape[:2][0]
    img_resize = cv2.resize(img, (size[0], size[1]), interpolation = cv2.INTER_CUBIC)
    GaussianBlur_img = cv2.GaussianBlur(img_resize, (3, 3), 0)#Gaussian Blur
    frame_lab = cv2.cvtColor(GaussianBlur_img, cv2.COLOR_BGR2LAB) #Convert the image into LAB space
    frame_mask = cv2.inRange(frame_lab,
                                 (lab_data[target_color]['min'][0],
                                  lab_data[target_color]['min'][1],
                                  lab_data[target_color]['min'][2]),
                                 (lab_data[target_color]['max'][0],
                                  lab_data[target_color]['max'][1],
                                  lab_data[target_color]['max'][2]))  #Perform bit operation on the original image and mask    
    opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))#Open
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((3,3),np.uint8))#close
    contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2] #Find all external contours
    areaMax_contour = getAreaMaxContour(contours, area_min=50)[0] #Find out the contour with the maximum area

    left_x, right_x, center_y, angle = -1, -1, -1, 0
    if areaMax_contour is not None:
        down_x = (areaMax_contour[areaMax_contour[:,:,1].argmax()][0])[0]
        down_y = (areaMax_contour[areaMax_contour[:,:,1].argmax()][0])[1]

        left_x = (areaMax_contour[areaMax_contour[:,:,0].argmin()][0])[0]
        left_y = (areaMax_contour[areaMax_contour[:,:,0].argmin()][0])[1]

        right_x = (areaMax_contour[areaMax_contour[:,:,0].argmax()][0])[0]
        right_y = (areaMax_contour[areaMax_contour[:,:,0].argmax()][0])[1]
        
        if pow(down_x - left_x, 2) + pow(down_y - left_y, 2) > pow(down_x - right_x, 2) + pow(down_y - right_y, 2):
            left_x = int(Misc.map(left_x, 0, size[0], 0, img_w))
            left_y = int(Misc.map(left_y, 0, size[1], 0, img_h))  
            right_x = int(Misc.map(down_x, 0, size[0], 0, img_w))
            right_y = int(Misc.map(down_y, 0, size[1], 0, img_h))
        else:
            left_x = int(Misc.map(down_x, 0, size[0], 0, img_w))
            left_y = int(Misc.map(down_y, 0, size[1], 0, img_h))
            right_x = int(Misc.map(right_x, 0, size[0], 0, img_w))
            right_y = int(Misc.map(right_y, 0, size[1], 0, img_h))

        center_y = int(Misc.map((areaMax_contour[areaMax_contour[:,:,1].argmax()][0])[1], 0, size[1], 0, img_h))
        angle = int(math.degrees(math.atan2(right_y - left_y, right_x - left_x)))
        
        cv2.line(img_draw, (left_x, left_y), (right_x, right_y), (255, 0, 0), 2)     
            
    return left_x, right_x, center_y, angle      


strp_up = True
#robot following thread 
def move():
    global object_center_y
    global strp_up
    
    while True:
        if switch:
            if object_center_y >= 300:  #The step is detected, then ajust the position slightly
                
                if 20 <= object_angle < 90:
                    AGC.runActionGroup(go_turn_right)
                    time.sleep(0.2)           
                elif -20 >= object_angle > -90:
                    AGC.runActionGroup(go_turn_left)
                    time.sleep(0.2)
                
                elif 3 < object_angle < 20:
                    AGC.runActionGroup(turn_right)
                    time.sleep(0.2)           
                elif -5 > object_angle > -20:
                    AGC.runActionGroup(turn_left)
                    time.sleep(0.2)
                    
                elif 300 <= object_center_y < 420:    #in center 
                    AGC.runActionGroup(go_forward_one_step)
                    time.sleep(0.2)
                    
                elif object_center_y >= 420: #close to the position and can hurdle or go up and down stairs
                    time.sleep(0.5)
                    if object_center_y >= 420:
                        setBuzzer(0.1) 
                        AGC.runActionGroup(go_forward_one_step) #move forward one step
                        time.sleep(0.2)
                    
                        if strp_up: # go up stair
                            AGC.runActionGroup('climb_stairs')
                            strp_up = False
                        else: # go down stair
                            AGC.runActionGroup(go_forward_one_step) #move forward one step
                            time.sleep(0.2)
                            AGC.runActionGroup('down_floor')
                            strp_up = True
                        time.sleep(0.5)
                        object_center_y = -1
                    
                else:
                    time.sleep(0.01)
            else:
                time.sleep(0.01)
        else:
            time.sleep(0.01)
                
            
#start as subthread 
th = threading.Thread(target=move)
th.setDaemon(True)
th.start()


def run(img):
    global object_left_x, object_right_x
    global object_center_y, object_angle
    
    img_copy = img.copy()
    img_h, img_w = img.shape[:2]
     
    # step
    object_left_x, object_right_x, object_center_y, object_angle = color_identify(img, img_copy, target_color = 'red')
    print('stairway',object_left_x, object_right_x, object_center_y, object_angle)
    # print angle positon paramter
    
            
        
    return img_copy

if __name__ == '__main__':
    
    from CameraCalibration.CalibrationConfig import *
    init()   
    
    #load parameter 
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
    if scale:
        Knew[(0,1), (0,1)] = scale * Knew[(0,1), (0,1)]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(k, d, np.eye(3), Knew, dim, cv2.CV_16SC2)
    
    camera = cv2.VideoCapture(-1)
    AGC.runAction('stand_slow')
    switch = True
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
    my_camera.camera_close()
    cv2.destroyAllWindows()

