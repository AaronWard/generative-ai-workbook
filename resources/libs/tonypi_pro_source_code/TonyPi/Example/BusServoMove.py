import time
import hiwonder.Board as Board

print('''
**********************************************************
********Function: Hiwonder TonyPi expansion board, serial port servo control routine*******
**********************************************************
----------------------------------------------------------
Official website:http://www.hiwonder.com
Online mall:https://huaner.tmall.com/
----------------------------------------------------------
The following commands need be opened in LX terminal by press "ctrl+alt+t" or clicking black LX terminal icon.
----------------------------------------------------------
Usage:
    python3 BusServoMove.py
----------------------------------------------------------
Version: --V1.2  2021/07/03
----------------------------------------------------------
Tips:
 * Press "Ctrl+C" close the running program, if fail to close, please try several times!
----------------------------------------------------------
''')

while True:
    # Parameter: parameter 1: servo ID; Parameter 2: position ; parameter 3: running time
    Board.setBusServoPulse(8, 500, 500) # It takes 500ms for No.8 servo to rotate to 500
    time.sleep(0.5) # The latency is the same as running time
    
    Board.setBusServoPulse(8, 200, 500) #The range of servo rotation is between 0° and 240° corresponding to 0-1000 pulse width, i.e, the range of parameter 2 is 0-1000
    time.sleep(0.5)
    
    Board.setBusServoPulse(8, 500, 200)
    time.sleep(0.2)
    
    Board.setBusServoPulse(8, 200, 500)  
    Board.setBusServoPulse(16, 200, 500)
    time.sleep(0.5)
    
    Board.setBusServoPulse(8, 500, 500)  
    Board.setBusServoPulse(16, 500, 500)
    time.sleep(0.5)    