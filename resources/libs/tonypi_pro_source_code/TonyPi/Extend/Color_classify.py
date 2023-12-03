#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/TonyPi/')
import cv2
import math
import time
import threading
import numpy as np
import hiwonder.Misc as Misc
import hiwonder.Board as Board
import hiwonder.Camera as Camera
import hiwonder.ActionGroupControl as AGC
import hiwonder.yaml_handle as yaml_handle

# color sorting 

debug = False

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

range_rgb = {
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'green': (0, 255, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
}

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

lab_data = None
servo_data = None
def load_config():
    global lab_data, servo_data
    
    lab_data = yaml_handle.get_yaml_data(yaml_handle.lab_file_path)
    servo_data = yaml_handle.get_yaml_data(yaml_handle.servo_file_path)

# Initial position
def initMove():
    Board.setBusServoPulse(17, 500, 500)
    Board.setBusServoPulse(19, 500, 500)
    Board.setPWMServoPulse(1, 1050, 500)
    Board.setPWMServoPulse(2, servo_data['servo2'], 500)

color_list = []
detect_color = 'None'
action_finish = True
draw_color = range_rgb["black"]

# Reset variable
def reset():
    global draw_color
    global color_list
    global detect_color
    global action_finish
    
    color_list = []
    detect_color = 'None'
    action_finish = True
    draw_color = range_rgb["black"]

__isRunning = False
# Initialization
def init():
    global __isRunning
    print("Init")
    load_config()
    initMove()
    reset()
    __isRunning = True

  
def runBuzzer(sleep):
    Board.setBuzzer(1) # Turn on 
    time.sleep(sleep) # Delay
    Board.setBuzzer(0) #Turn off 
 
def move():
    global draw_color
    global detect_color
    global action_finish
    
    
    while True:
        if debug:
            return
        if __isRunning:
            if detect_color != 'None':
                runBuzzer(0.1)
                action_finish = False
                
                time.sleep(1)
                if detect_color == 'red':
                    AGC.runActionGroup('grab_right')
                    detect_color = 'None'
                    draw_color = range_rgb["black"]                    
                    action_finish = True
                    
                elif detect_color == 'blue':
                    AGC.runActionGroup('grab_left')
                    detect_color = 'None'
                    draw_color = range_rgb["black"]                    
                    action_finish = True
                    
                elif detect_color == 'green':
                    for i in range(2):
                        Board.setPWMServoPulse(2, 1300, 300)
                        time.sleep(0.3)
                        Board.setPWMServoPulse(2, 1700, 300)
                        time.sleep(0.3)
                    Board.setPWMServoPulse(2, servo_data['servo2'], 500)
                    detect_color = 'None'
                    draw_color = range_rgb["black"]                    
                    action_finish = True
                    
                else:
                    detect_color = 'None'
                    draw_color = range_rgb["black"]                    
                    action_finish = True
            else:
               time.sleep(0.01)
        else:
            time.sleep(0.01)

# run subthread
th = threading.Thread(target=move)
th.setDaemon(True)
th.start()

size = (320, 240)
def run(img):
    global draw_color
    global color_list
    global detect_color
    global action_finish
    
    img_copy = img.copy()
    img_h, img_w = img.shape[:2]

    if not __isRunning:
        return img

    frame_resize = cv2.resize(img_copy, size, interpolation=cv2.INTER_NEAREST)
    frame_gb = cv2.GaussianBlur(frame_resize, (3, 3), 3)      
    frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # Convert the image into LAB space

    max_area = 0
    color_area_max = None    
    areaMaxContour_max = 0
    
    if action_finish:
        for i in lab_data:
            if i in ['red', 'green', 'blue']:
                frame_mask = cv2.inRange(frame_lab,
                                         (lab_data[i]['min'][0],
                                          lab_data[i]['min'][1],
                                          lab_data[i]['min'][2]),
                                         (lab_data[i]['max'][0],
                                          lab_data[i]['max'][1],
                                          lab_data[i]['max'][2]))  #Perform bit operation on the original image and mask
                eroded = cv2.erode(frame_mask, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))  #Erode
                dilated = cv2.dilate(eroded, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))) #Dilate
                if debug:
                    cv2.imshow(i, dilated)
                contours = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  #Find out the contour
                areaMaxContour, area_max = getAreaMaxContour(contours)  #Find out the maximum area
                if areaMaxContour is not None:
                    if area_max > max_area:#The maximum area is found
                        max_area = area_max
                        color_area_max = i
                        areaMaxContour_max = areaMaxContour
        if max_area > 3500:  # The maximum area is found
            ((centerX, centerY), radius) = cv2.minEnclosingCircle(areaMaxContour_max)  # Acquire the minimum circumscribed circle
            centerX = int(Misc.map(centerX, 0, size[0], 0, img_w))
            centerY = int(Misc.map(centerY, 0, size[1], 0, img_h))
            radius = int(Misc.map(radius, 0, size[0], 0, img_w))
            cv2.circle(img, (centerX, centerY), radius, range_rgb[color_area_max], 2)#Draw circle

            if color_area_max == 'red':  #Red area is the largest
                color = 1
            elif color_area_max == 'green':  #Green area is the largest
                color = 2
            elif color_area_max == 'blue':  #Blue area is the largest
                color = 3
            else:
                color = 0
            color_list.append(color)

            if len(color_list) == 3:  #Determine for multiple times
                # Take the average
                color = round(np.mean(np.array(color_list)))
                color_list = []
                if color == 1:
                    detect_color = 'red'
                    draw_color = range_rgb["red"]
                elif color == 2:
                    detect_color = 'green'
                    draw_color = range_rgb["green"]
                elif color == 3:
                    detect_color = 'blue'
                    draw_color = range_rgb["blue"]
                else:
                    detect_color = 'None'
                    draw_color = range_rgb["black"]               
        else:
            color_list = []
            detect_color = 'None'
            draw_color = range_rgb["black"]
            
    cv2.putText(img, "Color: " + detect_color, (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, draw_color, 2)
    
    return img


if __name__ == '__main__':
    from CameraCalibration.CalibrationConfig import *
    
    #Load parameter 
    param_data = np.load(calibration_param_path + '.npz')

    #obtain parameter
    dim = tuple(param_data['dim_array'])
    k = np.array(param_data['k_array'].tolist())
    d = np.array(param_data['d_array'].tolist())

    print('Parameter loading complete')

    #intercept area, 1 represents complete intercept
    scale = 1
    #optimize intrinsic parameters and distortion parameter
    p = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(k, d, dim ,None)
    Knew = p.copy()
    if scale:#change fov
        Knew[(0,1), (0,1)] = scale * Knew[(0,1), (0,1)]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(k, d, np.eye(3), Knew, dim, cv2.CV_16SC2)
  
    init()
    my_camera = Camera.Camera()
    my_camera.camera_open()
    AGC.runActionGroup('stand_slow')
    time.sleep(1)
    AGC.runActionGroup('squat_down')
    while True:
        img = my_camera.frame
        if img is not None:
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
    
    