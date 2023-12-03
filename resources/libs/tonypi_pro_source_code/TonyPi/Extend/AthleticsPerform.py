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
import hiwonder.ActionGroupControl as AGCs
import hiwonder.yaml_handle as yaml_handle

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

# Athletics performance 

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
    
    switch = False
    object_left_x, object_right_x, object_center_y, object_angle = -2, -2, -2, 0
    
def init():
    load_config()
    initMove()
    reset()

def setBuzzer(sleep):
    Board.setBuzzer(1) # Open
    time.sleep(sleep) # Latency
    Board.setBuzzer(0) # Close

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
            if contour_area_temp >= area_min:  # Only when the area is greater than the set value, the maximum contour is effective in order to avoid interference.
                area_max_contour = c

    return area_max_contour, contour_area_max  # Return the maximum contour


line_centerx = 320
size = (640, 480)
roi = [ (300, 340,  0, 640, 0.1), 
        (360, 400,  0, 640, 0.3), 
        (420, 480,  0, 640, 0.6)]
roi_h1 = roi[0][0]
roi_h2 = roi[1][0] - roi[0][0]
roi_h3 = roi[2][0] - roi[1][0]
roi_h_list = [roi_h1, roi_h2, roi_h3]

#Line following processing funciton
def line_patrol(img, img_draw, target_color = 'black'):
    
    n = 0
    center_ = []
    weight_sum = 0
    centroid_x_sum = 0
    
    img_h, img_w = img.shape[:2]
    frame_resize = cv2.resize(img_draw, size, interpolation=cv2.INTER_NEAREST)
    frame_gb = cv2.GaussianBlur(frame_resize, (3, 3), 3)   

    #Divide the image into upper, middle and lower parts for faster and more accurate processing.
    for r in roi:
        roi_h = roi_h_list[n]
        n += 1       
        blobs = frame_gb[r[0]:r[1], r[2]:r[3]]
        frame_lab = cv2.cvtColor(blobs, cv2.COLOR_BGR2LAB)  # Convert the image into LAB space
        
        area_max = 0
        areaMaxContour = 0
        frame_mask = cv2.inRange(frame_lab,
                                     (lab_data[target_color]['min'][0],
                                      lab_data[target_color]['min'][1],
                                      lab_data[target_color]['min'][2]),
                                     (lab_data[target_color]['max'][0],
                                      lab_data[target_color]['max'][1],
                                      lab_data[target_color]['max'][2]))  #Perform bit operation on the original image and mask                
        opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))  # Open
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))  # Close      
        cnts = cv2.findContours(closed , cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)[-2]#Find out all the contours
        cnt_large, area = getAreaMaxContour(cnts)#Find out the maximum contour
        if cnt_large is not None:#If the contour is not none
            rect = cv2.minAreaRect(cnt_large)#The minimum enclosing circle
            box = np.int0(cv2.boxPoints(rect))#The four vertice of the minimum enclosing circle
            for i in range(4):
                box[i, 1] = box[i, 1] + (n - 1)*roi_h + roi[0][0]
                box[i, 1] = int(Misc.map(box[i, 1], 0, size[1], 0, img_h))
            for i in range(4):                
                box[i, 0] = int(Misc.map(box[i, 0], 0, size[0], 0, img_w))
                
            cv2.drawContours(img_draw, [box], -1, (0,0,255,255), 2)#Draw the rectangle with four points
        
            #get the diagnol point of the rectangle
            pt1_x, pt1_y = box[0, 0], box[0, 1]
            pt3_x, pt3_y = box[2, 0], box[2, 1]            
            center_x, center_y = (pt1_x + pt3_x) / 2, (pt1_y + pt3_y) / 2#center pint
            cv2.circle(img_draw, (int(center_x), int(center_y)), 5, (0,0,255), -1)#draw the center point 
            
            center_.append([center_x, center_y])                        
            #sum the centers of upper, middle and lower parts according to different weights 
            centroid_x_sum += center_x * r[4]
            weight_sum += r[4]

    if weight_sum is not 0:
        #get the final centre
        line_centerx = int(centroid_x_sum / weight_sum)
        cv2.circle(img_draw, (line_centerx, int(center_y)), 10, (0,255,255), -1)#drew center
    else:
        line_centerx = 8888

    return line_centerx


# Colored block positioning process function
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
    opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))#open 
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((3,3),np.uint8))#close 
    contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2] #Find out all the contours
    areaMax_contour = getAreaMaxContour(contours, area_min=50)[0] #Find out the maximum contour

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


skip = 1
skip_st = True
items = None
line_st = True
fence_st = True
strp_up = True
x_center = 330
#Robot following thread 
def move():
    global object_center_y,line_centerx,items
    global line_st,strp_up,fence_st,skip_st
    
    while True:
        if switch:
            if object_center_y >= 300:  #the step or hurdle is detected, then adjust the position
                
                if 20 <= object_angle < 90:
                    AGC.runActionGroup(go_turn_right)
                    time.sleep(0.2)           
                elif -20 >= object_angle > -90:
                    AGC.runActionGroup(go_turn_left)
                    time.sleep(0.2)
                
                elif line_centerx - x_center > 15:
                    AGC.runAction(right_move)
                elif line_centerx - x_center < -15:
                    AGC.runAction(left_move)
                
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
                        AGC.runActionGroup(go_forward_one_step) #move forward one step
                        time.sleep(0.2)
                        
                        if items == 'hurdles':# hurdle 
                            
                            AGC.runActionGroup('hurdles')
                            skip_st = True
                            strp_up = True
                            items = None
                        elif items == 'stairway':
                            if strp_up: # go up stair
                                AGC.runActionGroup('climb_stairs')
                                strp_up = False
                            else: # go down stair 
                                AGC.runActionGroup(go_forward_one_step)
                                time.sleep(0.2)
                                AGC.runActionGroup('down_floor')
                                strp_up = True
                            items = None
                            skip_st = True
                        time.sleep(0.5)
                        object_center_y = -1
                    
                else:
                    time.sleep(0.01)
                    
            elif line_st and line_centerx != 8888: #line following 
                if abs(line_centerx - x_center) <= 20:
                    AGC.runAction(go_forward)
                    time.sleep(0.2)
                elif line_centerx - x_center > 20:
                    AGC.runAction(go_turn_right)
                    time.sleep(0.2)
                elif line_centerx - x_center < -20:
                    AGC.runAction(go_turn_left)
                    time.sleep(0.2)
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
    global skip_st, line_st, strp_st, fence_st
    global object_left_x, object_right_x, skip, items
    global object_center_y, object_angle, line_centerx
    
    img_copy = img.copy()
    img_h, img_w = img.shape[:2]
    
    # line following 
    line_centerx = line_patrol(img, img_copy, target_color = 'black') 
    
    # hurdle 
    if skip == 1:
        object_left_x, object_right_x, object_center_y, object_angle = color_identify(img, img_copy, target_color = 'blue')
        print('hurdles',object_left_x, object_right_x, object_center_y, object_angle)# print position angle parameter
        if object_center_y >= 260:#Ready to hurdle and close the detection for error frame 
            skip_st = False
            items = 'hurdles'
        elif object_center_y == -1:
            skip_st = True

    # step
    elif skip == 2:
        object_left_x, object_right_x, object_center_y, object_angle = color_identify(img, img_copy, target_color = 'red')
        print('stairway',object_left_x, object_right_x, object_center_y, object_angle)# print angle positon paramter
        if object_center_y >= 260:#Ready to hurdle and close the detection for error frame 
            skip_st = False
            items = 'stairway'
        elif object_center_y == -1:
            skip_st = True
               
    if skip_st: # set the error frame detection for hurdle and step
        skip += 1 
        if skip > 2:
            skip = 1
        
    return img_copy

if __name__ == '__main__':
    
    from CameraCalibration.CalibrationConfig import *
    init()   
    
    #load parameter 
    param_data = np.load(calibration_param_path + '.npz')

    #get parameter 
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

