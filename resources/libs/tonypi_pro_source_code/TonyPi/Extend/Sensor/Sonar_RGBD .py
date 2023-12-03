#!/usr/bin/env python3
import os
import sys
import time
import hiwonder.Sonar as Sonar

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

print('''
**********************************************************
********功能:幻尔科技树莓派扩展板，超声波传感器实验例程*********
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

s = Sonar.Sonar()
s.setRGBMode(0)    #设置灯的模式，0为彩灯模式，1为呼吸灯模式
s.setRGB(1, (35,205,55))
s.setRGB(0, (235,205,55))
s.startSymphony()

if __name__ == "__main__":
    while True:
        time.sleep(1)
        if s.getDistance() != 99999:
            print("Distance:", s.getDistance() , "mm")
            distance = s.getDistance()
            
            if 0.0 <= distance <= 100.0:
                s.setRGBMode(0)
                s.setRGB(1, (255,0,0))  #两边RGB设置为红色
                s.setRGB(0, (255,0,0))
                
            if 100.0 < distance <= 150.0:
                s.setRGBMode(0)
                s.setRGB(1, (0,255,0))  #两边RGB设置为绿色
                s.setRGB(0, (0,255,0))
                
            if 150.0 < distance <= 200.0:
                s.setRGBMode(0)
                s.setRGB(1, (0,0,255))  #两边RGB设置为蓝色
                s.setRGB(0, (0,0,255))
                
            if distance > 200.0:
                s.setRGBMode(0)      
                s.setRGB(1, (255,255,255)) # 两边RGB设置为白色
                s.setRGB(0, (255,255,255))
