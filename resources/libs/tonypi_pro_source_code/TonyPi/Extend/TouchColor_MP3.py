#!/usr/bin/env python3
import os
import sys
import time
import signal
import threading
import RPi.GPIO as GPIO
sys.path.append('/home/pi/TonyPi/')
import hiwonder.MP3 as MP3
import hiwonder.Board as Board
import hiwonder.ActionGroupControl as AGC
import hiwonder.yaml_handle as yaml_handle


if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

# Touch control dancing 

move_st = True
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


def setBuzzer(sleeptime):
    GPIO.setup(31, GPIO.OUT) #set pin as  output mode, BOARD code 31 corresponds to BCM code 6
    GPIO.output(31, 1)       #set pin to output high level
    time.sleep(sleeptime)   #set latency
    GPIO.output(31, 0)
    
def Stop(signum, frame):
    global move_st
    print('closing...')
    move_st = False
    mp3.pause() #pause

num = 0
time_ = 0
touch = False
state = True
pause_en = False
Timewait = False

def move(num_):
    global pause_en
    print(num)
    if num_ == '1':
        pause_en = True
        mp3.volume(10) #set the volume as 30 before playing 
        mp3.playNum(18) #play song 18
        time.sleep(0.8)
        AGC.runActionGroup('18')
    elif num_ == '2':
        pause_en = True
        mp3.volume(10) 
        mp3.playNum(22) 
        time.sleep(0.8)
        AGC.runActionGroup('22')
    elif num_ == '3':
        pause_en = True
        mp3.volume(10) 
        mp3.playNum(24) 
        time.sleep(0.8)
        AGC.runActionGroup('24')
    else:
        time.sleep(0.3)
        setBuzzer(0.2)
        time.sleep(0.1)
        setBuzzer(0.2)
    
    pause_en = False

if __name__ == "__main__":  
    
    addr = 0x7b         #sensor IIC address
    mp3 = MP3.MP3(addr)
    AGC.runActionGroup('stand_slow')
    initMove()
    
    while move_st:
        GPIO.setup(26, GPIO.IN) #set pin as output mode, Board code corresponds to BCM code 7
        touch = GPIO.input(26)  #read pin value
        
        if touch:
           state = True
           
        elif not touch and state:
            num += 1
            state = False
            setBuzzer(0.05)   #set buzzer to make sound 
            if num == 1:
                Timewait = True
                time_ = time.time()
            time.sleep(0.1)
                
        if Timewait:
            if int(time.time() - time_) >= 1 :
                if not pause_en:
                    th = threading.Thread(target=move, args=str(num), daemon=True)
                    th.start()
                    num = 0
                    Timewait = False
                    
                elif pause_en:
                    print('pause')
                    num = 0
                    pause_en = False
                    Timewait = False
                    mp3.pause() #pause
                    AGC.stopAction()
                    time.sleep(0.5)
                    AGC.runActionGroup('stand_slow')
        else:        
            time.sleep(0.01)
    
    