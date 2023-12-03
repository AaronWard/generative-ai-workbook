import time
import hiwonder.Board as Board

print('''
**********************************************************
********Function: Hiwonder TonyPi expansion board, Buzzer Control Routine*********
**********************************************************
----------------------------------------------------------
Official website:http://www.hiwonder.com
Online mall:https://huaner.tmall.com/
----------------------------------------------------------
The following commands need be opened in LX terminal by press "ctrl+alt+t" or clicking black LX terminal icon.
----------------------------------------------------------
Usage:
    python3 BuzzerControlDemo.py
----------------------------------------------------------
Version: --V1.2  2021/07/03
----------------------------------------------------------
Tips:
 * Press "Ctrl+C" close the running program, if fail to close, please try several times!
----------------------------------------------------------
''')

Board.setBuzzer(0) # close 

Board.setBuzzer(1) # open
time.sleep(0.1) # delay
Board.setBuzzer(0) #close

time.sleep(1) # delay

Board.setBuzzer(1)
time.sleep(0.5)
Board.setBuzzer(0)