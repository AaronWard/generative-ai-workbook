import time
import hiwonder.Board as Board

print('''
**********************************************************
*****Function: Hiwonder TonyPi expansion board, serial port servo reading status routine******
**********************************************************
----------------------------------------------------------
Official website:http://www.hiwonder.com
Online mall:https://huaner.tmall.com/
----------------------------------------------------------
The following commands need be opened in LX terminal by press "ctrl+alt+t" or clicking black LX terminal icon.
----------------------------------------------------------
Usage:
    python3 BusServoReadStatus.py
----------------------------------------------------------
Version: --V1.2  2021/07/03
----------------------------------------------------------
Tips:
 * Press "Ctrl+C" close the running program, if fail to close, please try several times!
----------------------------------------------------------
''')

def getBusServoStatus():
    Pulse = Board.getBusServoPulse(8) # get the position information of No.8 servo.
    Temp = Board.getBusServoTemp(8) # get the temperature information of No.8 servo
    Vin = Board.getBusServoVin(8) # get the voltage information of No.8 servo
    print('Pulse: {}\nTemp:  {}℃\nVin:   {}mV\n'.format(Pulse, Temp, Vin)) # print the status information
    time.sleep(0.5) # latency for checking

while True:   
    Board.setBusServoPulse(8, 500, 1000) # It takes 1000ms for No.8 servo to rotate to 500
    time.sleep(1)
    getBusServoStatus()
    Board.setBusServoPulse(8, 300, 1000)
    time.sleep(1)
    getBusServoStatus()