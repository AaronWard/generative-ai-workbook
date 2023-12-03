import os
import sys
import time
import signal
import hiwonder.MP3 as MP3

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

print('''
**********************************************************
********功能:幻尔科技树莓派扩展板，MP3模块实验例程*********
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

move_st = True
addr = 0x7b         #MP3 module address
mp3 = MP3.MP3(addr)

def Stop(signum, frame):
    global move_st
    move_st = False
    mp3.pause() #pause song play
    print('\n')

signal.signal(signal.SIGINT, Stop)

skip = True

if __name__ == "__main__":
    while move_st:
        if skip:
            mp3.volume(30) #set the volume to 30, please set before play.  
            mp3.playNum(18) #play song num0018
            skip = False
        else:
            time.sleep(0.05)
        
