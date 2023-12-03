#!/usr/bin/env python3
import os
import sys
sys.path.append('/home/pi/TonyPi/')
import time
import threading
import numpy as np
import RPi.GPIO as GPIO
import hiwonder.Board as Board
import hiwonder.Sonar as Sonar
import hiwonder.ActionGroupControl as AGC

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

# obstacle avoidance 

def setBuzzer(sleeptime):
    GPIO.setup(31, GPIO.OUT) #Set the pin to output mode, BOARD code 31 corresponds to BCM code 6
    GPIO.output(31, 1)       #set the pin to outout high level.
    time.sleep(sleeptime)    #set latencyncy
    GPIO.output(31, 0)

# left hand up
def hand_up():
    Board.setBusServoPulse(8,330,1000)
    time.sleep(0.3)
    Board.setBusServoPulse(7,860,1000)
    Board.setBusServoPulse(6,860,1000)
    time.sleep(1)
# left hand down
def hand_down():
    Board.setBusServoPulse(7,800,1000)
    Board.setBusServoPulse(6,575,1000)
    time.sleep(0.3)
    Board.setBusServoPulse(8,725,1000)
    time.sleep(1)
# stretch out left hand from the left side
def hand_left():
    Board.setBusServoPulse(8,330,1000)
    time.sleep(0.3)
    Board.setBusServoPulse(7,420,1000)
    Board.setBusServoPulse(6,920,1000)
    time.sleep(1)

distance = 99999
#robot movement subthread
def move():
    global distance
    
    dist_left = []
    dist_right = []
    distance_left = 99999
    distance_right = 99999
    
    while True:
        if distance != 99999:
            if distance <= 300: #detect the obstacle ahead
                distance = 99999
                hand_left() #stretch out left hand from the left side
                time.sleep(1)
                #consecutive detection three times 
                for i in range(3):
                    dist_left.append(distance)
                    time.sleep(0.05)
                #take average
                distance_left = round(np.mean(np.array(dist_left)))
                dist_left = []
                hand_up()
                
                if distance_left <= 300: #detect the left obstacle
                    distance_left = 99999
                    hand_down() # put down left hand 
                    for i in range(5): #turn right 
                        AGC.runActionGroup('turn_right')
                        time.sleep(0.2)
                        
                    hand_up()
                    time.sleep(1)
                    # consecutive right detection three times
                    for i in range(3):
                        dist_right.append(distance)
                        time.sleep(0.05)
                        
                    distance_right = round(np.mean(np.array(dist_right)))
                    dist_right = []
                    
                    if distance_right <= 300: #detect the obstacle on the right
                        distance_right = 99999
                        hand_down()
                        for i in range(5): #turn left
                            AGC.runActionGroup('turn_left')
                            time.sleep(0.2)
                            
                        for i in range(5):# move back
                            AGC.runActionGroup('back')
                        hand_up()
                    else: #If there is no abstacle on the right,move forward and then turn right
                        AGC.runActionGroup('go_hand_up')            
                else: #If there is no obstacle on the left, turn left
                    hand_down()
                    for i in range(5):
                        AGC.runActionGroup('turn_left')
                        time.sleep(0.2)
                    hand_up()
            else:#If there is no abstacle ahead, move forward 
                AGC.runActionGroup('go_hand_up')
        else:   
            time.sleep(0.01)
            
#start as subthread
th = threading.Thread(target=move)
th.setDaemon(True)
th.start()

if __name__ == "__main__":
    
    distance_list = []
    s = Sonar.Sonar()
    s.startSymphony()
    
    AGC.runActionGroup('stand_slow')
    time.sleep(1)
    hand_up()
    
    while True:
        
        distance_list.append(s.getDistance())
        
        #consecutive detection 6 times and take average
        if len(distance_list) >= 6: 
            distance = int(round(np.mean(np.array(distance_list))))
            print(distance, 'mm')
            distance_list = []
            
        time.sleep(0.01)
            
        
                       
    
