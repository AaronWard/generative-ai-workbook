#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/TonyPi/')
import cv2
import math
import time
import threading
import numpy as np
import hiwonder.ASR as ASR
import hiwonder.Misc as Misc
import hiwonder.Board as Board
import hiwonder.ActionGroupControl as AGC
import hiwonder.yaml_handle as yaml_handle

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

#voice control gripping 

asr = ASR.ASR()
CentreX = 330
state = False
target_color = 'None'
color, color_x, color_y, angle = None, 0, 0, 0

lab_data = None
def load_config():
    global lab_data
    lab_data = yaml_handle.get_yaml_data(yaml_handle.lab_file_path)
    
range_rgb = {
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'green': (0, 255, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'None': (255, 255, 255)}

# initial position
def initMove():
    Board.setPWMServoPulse(1, 980, 1000)
    Board.setPWMServoPulse(2, 1530, 1000)
    Board.setBusServoPulse(17, 500, 1000)
    Board.setBusServoPulse(18, 500, 1000)

    
def runBuzzer(sleep):
    Board.setBuzzer(1) # Turn on 
    time.sleep(sleep) # Delay
    Board.setBuzzer(0) #Turn off

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
            if contour_area_temp > 50:  
            # Only when the area is greater than 50, the maximum contour is effective in order to avoid interference.
                area_max_contour = c

    return area_max_contour, contour_area_max  # Return the maximum contour


def move():
    global state, target_color
    
    skip = True
    pulse2 = 1530
    dire = None
    while True:
        if state:
            if color is not 'None':
                if dire is None:
                    if color_x > CentreX:
                        dire = 'right'
                    elif color_x < CentreX:
                        dire = 'left'
                if 15 > color_x - CentreX > 8:
                    AGC.runAction('right_move_10')
                elif -15 < color_x - CentreX < -8:
                    AGC.runAction('left_move_10')
                elif color_x - CentreX >= 20:
                    AGC.runAction('right_move_20')
                elif color_x - CentreX <= -20:
                    AGC.runAction('left_move_20')
                else:
                    runBuzzer(0.1)
                    if dire == 'left':
                        AGC.runAction('grab_squat_left')
                        time.sleep(0.5)
                        AGC.runAction('grab_squat_up_left')
                        time.sleep(0.5)
                        AGC.runAction('grab_stand_left')
                    elif dire == 'right':
                        AGC.runAction('grab_squat_right')
                        time.sleep(0.5)
                        AGC.runAction('grab_squat_up_right')
                        time.sleep(0.5)
                        AGC.runAction('grab_stand_right')
                    dire = None
                    state = False
                    target_color = 'None'
                    
                if pulse2 - 1530 >= 10:
                    pulse2 -= 20
                elif pulse2 - 1530 <= -10:
                    pulse2 += 20
                Board.setPWMServoPulse(2, pulse2, 30)
                
            else:
                dire = None
                if skip:
                    pulse2 = 1700
                    skip = False
                else:
                    pulse2 = 1360
                    skip = True
                Board.setPWMServoPulse(2, pulse2, 300)
                time.sleep(0.8)
        else: 
            time.sleep(0.01)

# Run subthtread
th = threading.Thread(target=move)
th.setDaemon(True)
th.start()

def colorDetect(img):
    img_h, img_w = img.shape[:2]
    size = (img_w, img_h)
    frame_resize = cv2.resize(img, size, interpolation=cv2.INTER_NEAREST)
    frame_gb = cv2.GaussianBlur(frame_resize, (3, 3), 3)   
    frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # Convert the image into LAB space
    center_max_distance = pow(img_w/2, 2) + pow(img_h, 2)
    color, center_x, center_y, angle = 'None', -1, -1, 0
    if target_color != 'None':
        frame_mask = cv2.inRange(frame_lab,
                                 (lab_data[target_color]['min'][0],
                                  lab_data[target_color]['min'][1],
                                  lab_data[target_color]['min'][2]),
                                 (lab_data[target_color]['max'][0],
                                  lab_data[target_color]['max'][1],
                                  lab_data[target_color]['max'][2]))  
                                 #Perform bit operation on the original image and mask            
        eroded = cv2.erode(frame_mask, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))  #Erode
        dilated = cv2.dilate(eroded, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))) #Dilate
        contours = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # Find out the contour
        areaMaxContour, area_max = getAreaMaxContour(contours)  # Find out the maximum contour
        if area_max > 500:  # The maximum area is found
            rect = cv2.minAreaRect(areaMaxContour)#The minimum enclosing rectangle
            angle_ = rect[2]

            box = np.int0(cv2.boxPoints(rect))#The four vertice of the minimum enclosing rectangle 
            for j in range(4):
                box[j, 0] = int(Misc.map(box[j, 0], 0, size[0], 0, img_w))
                box[j, 1] = int(Misc.map(box[j, 1], 0, size[1], 0, img_h))
            cv2.drawContours(img, [box], -1, range_rgb[target_color], 2)
            #Draw a rectangle with four points 
            #Get the diagonal point of rectangle
            ptime_start_x, ptime_start_y = box[0, 0], box[0, 1]
            pt3_x, pt3_y = box[2, 0], box[2, 1]            
            center_x_, center_y_ = int((ptime_start_x + pt3_x) / 2), int((ptime_start_y + pt3_y) / 2)#center point    
            cv2.circle(img, (center_x_, center_y_), 5, (0, 255, 255), -1)#draw the center point 
            distance = pow(center_x_ - img_w/2, 2) + pow(center_y_ - img_h, 2)
            if distance < center_max_distance:  # find the closest object and transport
                center_max_distance = distance
                color = target_color
                center_x, center_y, angle = center_x_, center_y_, angle_
                    
    return color, center_x, center_y, angle

def run(img):
    global target_color, state
    global color, color_x, color_y, angle
    
    if not state:
        data = asr.getResult()
        if data:
            print("result:", data)
            if data == 2:
                target_color = 'red'
                state = True
            elif data == 3:
                target_color = 'green'
                state = True
            elif data == 4:
                target_color = 'blue'
                state = True
            else:
                target_color = 'None'
                state = False
            
    if state and target_color != 'None':
        color, color_x, color_y, angle = colorDetect(img)
#         print('Color:',color, color_x, color_y, angle)
        cv2.putText(img, "Color:"+color, (10, img.shape[0] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.65, range_rgb[color], 2)
       
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
    
    asr.eraseWords()
    asr.setMode(2)
    asr.addWords(1, 'kai shi')
    asr.addWords(2, 'na hong se')
    asr.addWords(3, 'na lv se')
    asr.addWords(4, 'na lan se')
    
    initMove()
    load_config()
    camera = cv2.VideoCapture(-1)
    AGC.runActionGroup('stand_slow')
    
    while True:
        ret,img = camera.read()
        if ret:
            Time = time.time()
            frame = img.copy()
            frame = cv2.remap(frame.copy(), map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
            Frame = run(frame)
            d_time = time.time() - Time
            fps = int(1.0 / d_time)
            cv2.putText(Frame, 'FPS:'+ str(fps), (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)
            cv2.imshow('Frame', Frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
        else:
            time.sleep(0.01)
    setFan(0)
    my_camera.camera_close()
    cv2.destroyAllWindows()
    
    
