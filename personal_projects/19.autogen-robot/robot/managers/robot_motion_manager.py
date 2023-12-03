"""
This script is a manager object for interacting
with a Chroma Database

Written by: Aaron Ward - 17nd November 2023
"""

import sys
import threading
from hiwonder.Board import *
import hiwonder.ActionGroupControl as AGC

class RobotMotionManager:
    def __init__(self, model):
        self._model = model

    def tpose(self, model):
        pass
    
    def kneel(self, model):
        pass

    def getServoPulse(id):
        return getBusServoPulse(id)

    def getServoDeviation(id):
        return getBusServoDeviation(id)

    def setServoPulse(id, pulse, use_time):
        setBusServoPulse(id, pulse, use_time)

    def setServoDeviation(id ,dev):
        setBusServoDeviation(id, dev)
        
    def saveServoDeviation(id):
        saveBusServoDeviation(id)

    def unloadServo(id):
        unloadBusServo(id)


    def runActionGroup(num):
        threading.Thread(target=AGC.runAction, args=(num, )).start()    

    def stopActionGroup():    
        AGC.stopAction()  

