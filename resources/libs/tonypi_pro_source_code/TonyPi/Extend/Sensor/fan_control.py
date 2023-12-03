#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/TonyPi/')
import time
import RPi.GPIO as GPIO
import hiwonder.Board as Board

#fan module experiment  

#GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BCM)

print('''
**********************************************************
********功能:幻尔科技树莓派扩展板，风扇模块实验例程*********
**********************************************************
----------------------------------------------------------
Official website:http://www.lobot-robot.com/pc/index/index
Online mall:https://lobot-zone.taobao.com/
Version: --V1.0  2021/12/10
----------------------------------------------------------
Tips:
 * 按下Ctrl+C可关闭此次程序运行，若失败请多次尝试！
----------------------------------------------------------
''')

# initial         
def init():
    start = False
    setFan(0)
    print("Fan Control Init")	
    
#fan control 
def setFan(start):
    GPIO.setup(24, GPIO.OUT) # correspond Expansion board GPIO8
    GPIO.setup(26, GPIO.OUT) # correspond Expansion board GPIO7             
    if start == 1:
        GPIO.output(24, 1)     
        GPIO.output(26, 0)       
    else:
        GPIO.output(24, 0)
        GPIO.output(26, 0)           

if __name__ == '__main__': 
    while True:
        try:
            setFan(1)
        except KeyboardInterrupt:
            setFan(0)
            break
    
    
