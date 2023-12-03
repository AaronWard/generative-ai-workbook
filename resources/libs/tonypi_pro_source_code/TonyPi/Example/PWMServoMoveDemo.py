import time
import hiwonder.Board as Board

print('''
**********************************************************
********Function: Hiwonder TonyPi expansion board, PWM servo control routine********
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
    # Parameter: parameter 1: the port number of the connected servo; parameter 2: position; parapmeter 3: running time
    Board.setPWMServoPulse(2, 1500, 500) # It takes 500ms for the No. 2 servo to rotate to 1500
    time.sleep(0.5) # The latency time is the same as running time
    
    Board.setPWMServoPulse(2, 1800, 500) #Servo rotates between the range of 0° and 180° corresponding to 500-2500 pulse width, i.e, the range of servo rotation is 500 to 2500
    time.sleep(0.5)
    
    Board.setPWMServoPulse(2, 1500, 200)
    time.sleep(0.2)
    
    Board.setPWMServoPulse(2, 1800, 500)  
    Board.setPWMServoPulse(1, 1800, 500)
    time.sleep(0.5)
    
    Board.setPWMServoPulse(2, 1500, 500)  
    Board.setPWMServoPulse(1, 1500, 500)
    time.sleep(0.5)    