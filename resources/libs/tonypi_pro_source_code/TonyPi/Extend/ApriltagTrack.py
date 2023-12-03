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
import hiwonder.apriltag as apriltag
import hiwonder.ActionGroupControl as AGC
import hiwonder.yaml_handle as yaml_handle

#place in Apriltag area 

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

debug = False
tag_id = None
action_finish = False
CentreX = 320
servo1, servo2 = 920, 1500
objective_x, objective_y = 0, 0
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

# Initial position
def initMove():
    Board.setPWMServoPulse(1, servo1, 1000)
    Board.setPWMServoPulse(2, servo2, 1000)
    Board.setBusServoPulse(17, 500, 1000)
    Board.setBusServoPulse(18, 500, 1000)

def right_splay():
    Board.setBusServoPulse(17, 240, 1000)
    time.sleep(1)
    
def right_grasp():
    Board.setBusServoPulse(17, 500, 1000)
    time.sleep(1)
    
def up_hand():
    Board.setBusServoPulse(16, 650, 1000)
    time.sleep(0.5)
    Board.setBusServoPulse(15, 260, 1000)
    Board.setBusServoPulse(14, 180, 1000)
    Board.setBusServoPulse(19, 260, 1000)
    time.sleep(1)

def down_hand():
    Board.setBusServoPulse(15, 200, 1000)
    Board.setBusServoPulse(14, 460, 1000)
    Board.setBusServoPulse(19, 500, 1000)
    time.sleep(0.6)
    Board.setBusServoPulse(16, 275, 1000)
    time.sleep(1)
    
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
            if contour_area_temp > 50:  # Only when the area is greater than 50, the maximum contour is effective in order to avoid interference.
                area_max_contour = c

    return area_max_contour, contour_area_max  # Return the maximum contour


def move():
    global tag_id,objective_x,objective_y
    global action_finish,servo1,servo2
    
    LOCK_servos = {'14': 180,'15': 260,'16': 650}
    servo1_st, servo2_st = True, True
    
    while True:
        if not action_finish:
            if color is not None:
                if color_y >= 300:
                    runBuzzer(0.1)
                    up_hand()
                    right_splay()
                    time.sleep(2)
                    runBuzzer(0.1)
                    time.sleep(0.1)
                    runBuzzer(0.1)
                    right_grasp()
                    down_hand()
                    action_finish = True
                else:
                    time.sleep(0.01)
            else:
                time.sleep(0.01)
                    
        elif action_finish:
            if tag_id is not None:
                if objective_x - CentreX >= 50 and objective_y < 240:
                    AGC.runAction('turn_right')
                    
                elif objective_x - CentreX <= -50 and objective_y < 240:
                    AGC.runAction('turn_left')
                
                elif objective_y <= 280:
                    AGC.runAction('go_forward')
                
                elif objective_x - CentreX >= 30:
                    AGC.runAction('right_move_20')
                    
                elif objective_x - CentreX <= -30:
                    AGC.runAction('left_move_20')
                
                elif 30 > objective_x - CentreX >= 10:
                    AGC.runAction('right_move')
                    
                elif -30 < objective_x - CentreX <= -10:
                    AGC.runAction('left_move')
                    
                elif 280 < objective_y < 320:
                    AGC.runAction('go_forward_one_step')
                
                elif objective_y >= 320:
                    runBuzzer(0.1)
                    AGC.runAction('put_down_object')
                    right_splay()
                    time.sleep(0.5)
                    right_grasp()
                    AGC.runAction('put_up_object')
                    time.sleep(2)
                    action_finish = False
                    
                if servo1 > 920:
                    servo1 -= 15
                servo1 = 920 if servo1 < 920 else servo1
                
                if servo2 - 1500 >= 10:
                    servo2 -= 10
                elif servo2 - 1500 <= -10:
                    servo2 +=10 
                        
                Board.setPWMServoPulse(1, servo1, 30)
                Board.setPWMServoPulse(2, servo2, 30)
                
            else:
                if servo1 >= 1250:
                    servo1_st = False
                elif servo1 <= 920:
                    servo1_st = True   
                if servo1_st:
                    servo1 += 5
                else:
                    servo1 -= 5
                    
                if servo2 >= 1700:
                    servo2_st = False
                elif servo2 <= 1300:
                    servo2_st = True
                    
                if servo2_st:
                    servo2 += 5
                else:
                    servo2 -= 5
                Board.setPWMServoPulse(1, servo1, 30)
                Board.setPWMServoPulse(2, servo2, 30)
                time.sleep(0.05)
                
        else:
            time.sleep(0.01)

# run subthread
th = threading.Thread(target=move)
th.setDaemon(True)
th.start()

# detect apriltag
detector = apriltag.Detector(searchpath=apriltag._get_demo_searchpath())

def apriltagDetect(img):   
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    detections = detector.detect(gray, return_image=False)

    if len(detections) != 0:
        for detection in detections:                       
            corners = np.rint(detection.corners)  # get four corner points
            cv2.drawContours(img, [np.array(corners, np.int)], -1, (0, 255, 255), 2)

            tag_family = str(detection.tag_family, encoding='utf-8')  # get tag_family
            tag_id = int(detection.tag_id)  # get tag_id

            objective_x, objective_y = int(detection.center[0]), int(detection.center[1])  # center point 
            
            object_angle = int(math.degrees(math.atan2(corners[0][1] - corners[1][1], corners[0][0] - corners[1][0])))  # calculate the rotation angle 
            
            return [tag_family, tag_id, objective_x, objective_y]
            
    return None, None, None, None


def colorDetect(img):
    img_h, img_w = img.shape[:2]
    size = (img_w, img_h)
    frame_resize = cv2.resize(img, size, interpolation=cv2.INTER_NEAREST)
    frame_gb = cv2.GaussianBlur(frame_resize, (3, 3), 3)   
    frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # Convert the image into LAB space
    
    center_max_distance = pow(img_w/2, 2) + pow(img_h, 2)
    color, center_x, center_y, angle = 'None', -1, -1, 0
    for i in lab_data:
        if i in color_list:
            frame_mask = cv2.inRange(frame_lab,
                                     (lab_data[i]['min'][0],
                                      lab_data[i]['min'][1],
                                      lab_data[i]['min'][2]),
                                     (lab_data[i]['max'][0],
                                      lab_data[i]['max'][1],
                                      lab_data[i]['max'][2]))  
                                     #Perform bit operation on the original image and mask            
            eroded = cv2.erode(frame_mask, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))  #Erode
            dilated = cv2.dilate(eroded, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))) #Dilate
            contours = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # Find out the contour
            areaMaxContour, area_max = getAreaMaxContour(contours)  # Find out the maximum contour
            
            if area_max > 500:  # The maximum area is found
                rect = cv2.minAreaRect(areaMaxContour)#The minimum bounding rectangle
                angle_ = rect[2]
        
                box = np.int0(cv2.boxPoints(rect))#The four vertice of the minimum bounding rectangle 
                for j in range(4):
                    box[j, 0] = int(Misc.map(box[j, 0], 0, size[0], 0, img_w))
                    box[j, 1] = int(Misc.map(box[j, 1], 0, size[1], 0, img_h))

                cv2.drawContours(img, [box], -1, range_rgb[i], 2)#Draw a rectangle with four points 
            
                #Get the diagonal point of rectangle
                ptime_start_x, ptime_start_y = box[0, 0], box[0, 1]
                pt3_x, pt3_y = box[2, 0], box[2, 1]            
                center_x_, center_y_ = int((ptime_start_x + pt3_x) / 2), int((ptime_start_y + pt3_y) / 2)#center point       
                cv2.circle(img, (center_x_, center_y_), 5, (0, 255, 255), -1)#draw the center point 
                
                distance = pow(center_x_ - img_w/2, 2) + pow(center_y_ - img_h, 2)
                if distance < center_max_distance:  # Find the closest object and transport
                    center_max_distance = distance
                    color = i
                    center_x, center_y, angle = center_x_, center_y_, angle_
                    
    return color, center_x, center_y, angle

def run(img):
    global tag_id,objective_x,objective_y
    global action_finish, color, color_x, color_y, angle
     
    img_copy = img.copy()
    img_h, img_w = img.shape[:2]
    
    if action_finish:
        tag_family, tag_id, objective_x, objective_y = apriltagDetect(img) # apriltag detection
        print('Apriltag:',objective_x,objective_y)
        if tag_id is not None:
            cv2.putText(img, "tag_id: " + str(tag_id), (10, img.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, [0, 255, 255], 2)
            cv2.putText(img, "tag_family: " + tag_family, (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, [0, 255, 255], 2)
        else:
            cv2.putText(img, "tag_id: None", (10, img.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, [0, 255, 255], 2)
            cv2.putText(img, "tag_family: None", (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, [0, 255, 255], 2)
        
    elif not action_finish:
        color, color_x, color_y, angle = colorDetect(img)
        print('Color:',color, color_x, color_y, angle)
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
  
    initMove()
    load_config()
    color_list = ('red','blue','green')
    camera = cv2.VideoCapture(-1)
    AGC.runActionGroup('stand_slow')
    
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
    
    
