#!/usr/bin/env python3
import os
import sys
import time
import hiwonder.tm1640 as tm

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

print('''
**********************************************************
********功能:幻尔科技树莓派扩展板，点阵模块实验例程*********
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

if __name__ == "__main__":  
    while True:
        try:
            ## display 'Hello'
            tm.display_buf = (0x7f, 0x08, 0x7f, 0x00, 0x7c, 0x54, 0x5c, 0x00,
                              0x7c, 0x40, 0x00,0x7c, 0x40, 0x38, 0x44, 0x38)

            tm.update_display()
            time.sleep(5)
        except KeyboardInterrupt:
            tm.display_buf = [0] * 16
            tm.update_display()
            break
            


