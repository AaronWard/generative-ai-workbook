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
import hiwonder.tm1640 as tm
import hiwonder.Board as Board
import hiwonder.Camera as Camera
import hiwonder.ActionGroupControl as AGC
import hiwonder.yaml_handle as yaml_handle


if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)
 
# The dot matrix displays shape 
# Sensor connection port：expansion board io7、io8
 
lab_data = None
servo_data = None
move_st = True

def load_config():
    global lab_data, servo_data
    
    lab_data = yaml_handle.get_yaml_data(yaml_handle.lab_file_path)
    servo_data = yaml_handle.get_yaml_data(yaml_handle.servo_file_path)
    
# initial position
def initMove():
    Board.setPWMServoPulse(1, 1350, 500)
    Board.setPWMServoPulse(2, servo_data['servo2'], 500)


# Find out the contour with the maximum area
# The parameter is the list of the contour to be compared
def getAreaMaxContour(contours):
    contour_area_temp = 0
    contour_area_max = 0
    area_max_contour = None

    for c in contours:  # loop all the contours
        contour_area_temp = math.fabs(cv2.contourArea(c))  # Calculate the contour area
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp > 50:  # Only when the area is greater than 50, the maximum contour is effective in order to avoid interference.
                area_max_contour = c

    return area_max_contour, contour_area_max  # Return the maximum contour

shape_length = 0

def run():
    global shape_length
    
    while move_st:
        if shape_length == 3:
            print('triangle')
            ## Display ‘triangle’
            tm.display_buf = (0x80, 0xc0, 0xa0, 0x90, 0x88, 0x84, 0x82, 0x81,
                              0x81, 0x82, 0x84,0x88, 0x90, 0xa0, 0xc0, 0x80)
            tm.update_display()
            
        elif shape_length == 4:
            print('rectangle')
            ## Display 'rectangle;
            tm.display_buf = (0x00, 0x00, 0x00, 0x00, 0xff, 0x81, 0x81, 0x81,
                              0x81, 0x81, 0x81,0xff, 0x00, 0x00, 0x00, 0x00)
            tm.update_display()
            
        elif shape_length >= 6:           
            print('circle')
            ## display ‘circle’
            tm.display_buf = (0x00, 0x00, 0x00, 0x00, 0x1c, 0x22, 0x41, 0x41,
                              0x41, 0x22, 0x1c,0x00, 0x00, 0x00, 0x00, 0x00)
            tm.update_display()
            
        else:
            ## clear screen
            tm.display_buf = [0] * 16
            tm.update_display()
            print('None')
            
       
        
# run subthread
th = threading.Thread(target=run)
th.setDaemon(True)
th.start()

shape_list = []
action_finish = True

def Stop(signum, frame):
    global move_st
    move_st = False
    tm.display_buf = [0] * 16
    tm.update_display()
    print('closing...')
    AGC.runActionGroup('lift_down')

signal.signal(signal.SIGINT, Stop)

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
    
    load_config()
    initMove()
    my_camera = Camera.Camera()
    my_camera.camera_open()
    AGC.runActionGroup('stand_slow')
    AGC.runActionGroup('lift_up')
    while move_st:
        img = my_camera.frame
        if img is not None:
            img_copy = img.copy()
            img_h, img_w = img.shape[:2]
            frame_gb = cv2.GaussianBlur(img_copy, (3, 3), 3)      
            frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # Convert the image into LAB space
            max_area = 0
            color_area_max = None    
            areaMaxContour_max = 0

            if action_finish:
                for i in lab_data:
                    if i != 'white' and i != 'black':
                        frame_mask = cv2.inRange(frame_lab,
                                         (lab_data[i]['min'][0],
                                          lab_data[i]['min'][1],
                                          lab_data[i]['min'][2]),
                                         (lab_data[i]['max'][0],
                                          lab_data[i]['max'][1],
                                          lab_data[i]['max'][2]))  #Perform bit operation on the original image and mask
                        opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6,6),np.uint8))  #Open 
                        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6,6),np.uint8)) #close 
                        contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  #Find out the contour
                        areaMaxContour, area_max = getAreaMaxContour(contours)  #Find out the maximum contour
                        if areaMaxContour is not None:
                            if area_max > max_area:#Find out the maximum area
                                max_area = area_max
                                color_area_max = i
                                areaMaxContour_max = areaMaxContour
            if max_area > 200:                   
                cv2.drawContours(img, areaMaxContour_max, -1, (0, 0, 255), 2)
                # Recognize shape
                # circumference  0.035 Modify based on the recognition situation. The btter the recognition, the smaller the value
                epsilon = 0.035 * cv2.arcLength(areaMaxContour_max, True)
                # the contour approximation
                approx = cv2.approxPolyDP(areaMaxContour_max, epsilon, True)
                shape_list.append(len(approx))
                if len(shape_list) == 30:
                    shape_length = int(round(np.mean(shape_list)))                            
                    shape_list = []
                    print(shape_length)
            # correct camera distortion
            img = cv2.remap(img.copy(), map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)  
            frame_resize = cv2.resize(img, (320, 240))
            cv2.imshow('frame', frame_resize)
            key = cv2.waitKey(1)
            if key == 27:
                break
        else:
            time.sleep(0.01)
    my_camera.camera_close()
    cv2.destroyAllWindows()

