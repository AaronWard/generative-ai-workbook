import sys
from hiwonder.Board import *

def getServoID():
    return getBusServoID()

def getServoPulse(id):
    return getBusServoPulse(id)

def getServoVin(id):
    return getBusServoVin(id)

def getServoTemp(id):
    return getBusServoTemp(id)

def getServoDeviation(id):
    return getBusServoDeviation(id)

def getServoTempLimit(id):
    return getBusServoTempLimit(id)

def getServoAngleLimit(id):
    return getBusServoAngleLimit(id)

def getServoVinLimit(id):
    return getBusServoVinLimit(id)

def setServoID(old_id, new_id):
    setBusServoID(old_id, new_id)

def setServoPulse(id, pulse, use_time):
    setBusServoPulse(id, pulse, use_time)

def setServoDeviation(id ,dev):
    setBusServoDeviation(id, dev)
    
def saveServoDeviation(id):
    saveBusServoDeviation(id)
    
def setServoMaxTemp(id, temp):
    setBusServoMaxTemp(id, temp)
  
def setServoVinLimit(id, vin_min, vin_max):
    setBusServoVinLimit(id, vin_min, vin_max)
  
def setServoAngleLimit(id, pulse_min, pulse_max):
    setBusServoAngleLimit(id, pulse_min, pulse_max)
