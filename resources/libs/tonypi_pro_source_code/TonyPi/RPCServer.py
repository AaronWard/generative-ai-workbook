#!/usr/bin/python3
# coding=utf8
import os
import sys
import time
import math
import logging
import threading

from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response

from jsonrpc import JSONRPCResponseManager, dispatcher

import hiwonder.Board as Board
import hiwonder.Mpu6050 as Mpu6050
import hiwonder.ActionGroupControl as AGC

from ActionGroupDict import action_group_dict

import Functions.Running as Running
import Functions.KickBall as KickBall
import Functions.Transport as Transport
import Functions.lab_adjust as lab_adjust
import Functions.ColorTrack as ColorTrack
import Functions.VisualPatrol as VisualPatrol

# remotely  call api, frameword jsonrpc
# mainly used for calling the client-end of mobile phone and computer

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

__RPC_E01 = "E01 - Invalid number of parameter!"
__RPC_E02 = "E02 - Invalid parameter!"
__RPC_E03 = "E03 - Operation failed!"
__RPC_E04 = "E04 - Operation timeout!"
__RPC_E05 = "E05 - Not callable"

Board.setBuzzer(1)
time.sleep(0.1)
Board.setBuzzer(0)
ColorTrack.initMove()
AGC.runActionGroup('stand_slow')

#mpu6050 initialization
mpu = Mpu6050.mpu6050(0x68)
mpu.set_gyro_range(mpu.GYRO_RANGE_2000DEG)
mpu.set_accel_range(mpu.ACCEL_RANGE_2G)

HWSONAR = None
QUEUE = None

# pwm servo control
# parameter 1: time (ms)
# parameter 2: the number of servos
# parameter 3: servo ID (1 or 2)
# parameter 4: servo position (500-2500)
# ...servo id
# ...servo position
# For example, [1000, 2, 1, 1500, 5, 1500]
@dispatcher.add_method
def SetPWMServo(*args, **kwargs):
    ret = (True, (), 'SetPWMServo')
    arglen = len(args)
    if 0 != (arglen % 2):
        return (False, __RPC_E01, 'SetPWMServo')
    try:
        servos = args[2:arglen:2]
        pulses = args[3:arglen:2]
        use_times = args[0]
        for s in servos:
            if s < 1 or s > 2:
                return (False, __RPC_E02, 'SetPWMServo')
        dat = zip(servos, pulses)
        for (s, p) in dat:
            Board.setPWMServoPulse(s, p, use_times)
    except Exception as e:
        print(e)
        ret = (False, __RPC_E03, 'SetPWMServo')
    return ret

# serial port servo control
# parameter 1: time (ms)
# parameter 2: the number of servos
# parameter 3: servo ID 
# parameter 4: servo position (500-2500)
# ...servo id
# ...servo position
# ...
# For example, [1000, 1, 1, 500]
@dispatcher.add_method
def SetBusServoPulse(*args, **kwargs):
    ret = (True, (), 'SetBusServoPulse')   
    arglen = len(args)
    if (args[1] * 2 + 2) != arglen or arglen < 4:
        return (False, __RPC_E01, 'SetBusServoPulse')
    try:
        servos = args[2:arglen:2]
        pulses = args[3:arglen:2]
        use_times = args[0]
        for s in servos:
           if s < 1 or s > 16:
                return (False, __RPC_E02, 'SetBusServoPulse')
        dat = zip(servos, pulses)
        for (s, p) in dat:
            Board.setBusServoPulse(s, p, use_times)
    except Exception as e:
        print(e)
        ret = (False, __RPC_E03, 'SetBusServoPulse')
    return ret

# Serial port servo deviation setting
# Parameter：servo deviation（-125-125）
@dispatcher.add_method
def SetBusServoDeviation(*args):
    ret = (True, (), 'SetBusServoDeviation')
    arglen = len(args)
    if arglen != 2:
        return (False, __RPC_E01, 'SetBusServoDeviation')
    try:
        servo = args[0]
        deviation = args[1]
        Board.setBusServoDeviation(servo, deviation)
    except Exception as e:
        print(e)
        ret = (False, __RPC_E03, 'SetBusServoDeviation')
    return ret

# Servo deviation reading
# Parameter：readDeviation
# Return：1-16 servo deviation
@dispatcher.add_method
def GetBusServosDeviation(args):
    ret = (True, (), 'GetBusServosDeviation')
    data = []
    if args != "readDeviation":
        return (False, __RPC_E01, 'GetBusServosDeviation')
    try:
        for i in range(1, 16):
            dev = Board.getBusServoDeviation(i)
            if dev is None:
                dev = 999
            data.append(dev)
        ret = (True, data, 'GetBusServosDeviation')
    except Exception as e:
        print(e)
        ret = (False, __RPC_E03, 'GetBusServosDeviation')
    return ret 

# Serial port servo deviation saving
# Parameter：downloadDeviation
@dispatcher.add_method
def SaveBusServosDeviation(args):
    ret = (True, (), 'SaveBusServosDeviation')
    if args != "downloadDeviation":
        return (False, __RPC_E01, 'SaveBusServosDeviation')
    try:
        for i in range(1, 16):
            dev = Board.saveBusServoDeviation(i)
    except Exception as e:
        print(e)
        ret = (False, __RPC_E03, 'SaveBusServosDeviation')
    return ret 

# servo powers off
# parameter：servoPowerDown
@dispatcher.add_method
def UnloadBusServo(args):
    ret = (True, (), 'UnloadBusServo')
    if args != 'servoPowerDown':
        return (False, __RPC_E01, 'UnloadBusServo')
    try:
        for i in range(1, 16):
            Board.unloadBusServo(i)
    except Exception as e:
        print(e)
        ret = (False, __RPC_E03i, 'UnloadBusServo')
    return ret

# get servo position
# Parameter：angularReadback
# Return：1-16 Servo Position
@dispatcher.add_method
def GetBusServosPulse(args):
    ret = (True, (), 'GetBusServosPulse')
    data = []
    if args != 'angularReadback':
        return (False, __RPC_E01, 'GetBusServosPulse')
    try:
        for i in range(1, 16):
            pulse = Board.getBusServoPulse(i)
            if pulse is None:
                ret = (False, __RPC_E04, 'GetBusServosPulse')
                return ret
            else:
                data.append(pulse)
        ret = (True, data, 'GetBusServosPulse')
    except Exception as e:
        print(e)
        ret = (False, __RPC_E03, 'GetBusServosPulse')
    return ret 

# Stop current action
# Parameter：stopAction
@dispatcher.add_method
def StopBusServo(args):
    ret = (True, (), 'StopBusServo')
    if args != 'stopAction':
        return (False, __RPC_E01, 'StopBusServo')
    try:     
        AGC.stopAction()
    except Exception as e:
        print(e)
        ret = (False, __RPC_E03, 'StopBusServo')
    return ret

# Stop running the current action group
# Parameter：stopActionGroup
@dispatcher.add_method
def StopActionGroup(args):
    ret = (True, (), 'StopActionGroup')
    if args != 'stopActionGroup':
        return (False, __RPC_E01, 'StopActionGroup')
    try:     
        AGC.stopActionGroup()
    except Exception as e:
        print(e)
        ret = (False, __RPC_E03, 'StopActionGroup')
    return ret

# action group running 
# Parameter1：Action number (character form)
# Parameter2：Number of actions (0 for looping)
# for example,['1', 2]
th = None
have_move = True
@dispatcher.add_method
def RunAction(*args_):
    global th
    global have_move 
    
    ret = (True, (), 'RunAction')
    actName = '0'
    times = 1
    
    if len(args_) != 2:
        return (False, __RPC_E01, 'RunAction')
    try:
        if args_[0] == '0':
            if have_move:
                AGC.stopActionGroup()
                have_move = False
        else:
            if th is not None:
                if not th.is_alive():
                    if args_[0] in action_group_dict:
                        actName = action_group_dict[args_[0]]
                    else:
                        actName = args_[0]
                    times = int(args_[1])
                    th = threading.Thread(target=AGC.runActionGroup, args=(actName, times))
                    th.start()
                    have_move = True
            else:
                if args_[0] in action_group_dict:
                    actName = action_group_dict[args_[0]]
                else:
                    actName = args_[0]
                times = int(args_[1])
                th = threading.Thread(target=AGC.runActionGroup, args=(actName, times))
                th.start()
                have_move = True
    except Exception as e:
        print(e)
        ret = (False, __RPC_E03, 'RunAction')
    return ret

# Fall stand up testing
def standup():
    count1 = 0
    count2 = 0
    count3 = 0
    for i in range(20):
        try:
            accel_date = mpu.get_accel_data(g=True) #get sensor value
            angle_y = int(math.degrees(math.atan2(accel_date['y'], accel_date['z']))) #convert into angle value
            
            #print(count1, count2, count3, angle_y)
            if abs(angle_y) > 160: 
                count1 += 1
            else:
                count1 = 0
            if abs(angle_y) < 10:
                count2 += 1
            else:
                count2 = 0
            time.sleep(0.1)
            count3 += 1
            if count3 > 5 and count1 < 3 and count2 < 3:
                break
            if count1 >= 10: #tilt back for a while and stand up
                count1 = 0
                AGC.runActionGroup('stand_up_back')
                break
            elif count2 >= 10: #Tilt forward for a while and get up
                count2 = 0
                AGC.runActionGroup('stand_up_front')
                break
        except BaseException as e:
            print(e)

# Fall and stand up calling 
th2 = None
@dispatcher.add_method
def StandUp():
    global th2

    ret = (True, (), 'StandUp')

    if th2 is not None:
        if not th2.is_alive():
            th2 = threading.Thread(target=standup)
            th2.start()
        else:
            pass
    else:
        th2 = threading.Thread(target=standup)
        th2.start()

    return ret

def runbymainth(req, pas):
    if callable(req):
        #print('pas', req)
        event = threading.Event()
        ret = [event, pas, None]
        QUEUE.put((req, ret))
        count = 0
        #ret[2] =  req(pas)
        #print('ret', ret)
        while ret[2] is None:
            time.sleep(0.01)
            count += 1
            if count > 200:
                break
        if ret[2] is not None:
            if ret[2][0]:
                return ret[2]
            else:
                return (False, __RPC_E03 + " " + ret[2][1])
        else:
            return (False, __RPC_E04)
    else:
        return (False, __RPC_E05)

@dispatcher.add_method
def LoadFunc(new_func = 0):
    return runbymainth(Running.loadFunc, (new_func, ))

@dispatcher.add_method
def UnloadFunc():
    return runbymainth(Running.unloadFunc, ())

@dispatcher.add_method
def StartFunc():
    return runbymainth(Running.startFunc, ())

@dispatcher.add_method
def StopFunc():
    return runbymainth(Running.stopFunc, ())

@dispatcher.add_method
def FinishFunc():
    return runbymainth(Running.finishFunc, ())

@dispatcher.add_method
def Heartbeat():
    return runbymainth(Running.doHeartbeat, ())

@dispatcher.add_method
def GetRunningFunc():
    #return runbymainth("GetRunningFunc", ())
    return (True, (0,))

# Set tracking color
# Parameter：color（red，green，blue）
# For example,[(red,)]
@dispatcher.add_method
def SetTargetTrackingColor(*target_color):
    return runbymainth(ColorTrack.setTargetColor, target_color)

# Set line color
# Parameter：color（red，green，blue）
# For example,[(red,)]
@dispatcher.add_method
def SetVisualPatrolColor(*target_color):
    return runbymainth(VisualPatrol.setLineTargetColor, target_color)

# set the ball color 
# Parameter：color（red，green，blue）
# For example,[(red,)]
@dispatcher.add_method
def SetBallColor(*target_color):
    return runbymainth(KickBall.setBallTargetColor, target_color)

# set color threshold 
# parameter: color lab
# For example,[{'red': ((0, 0, 0), (255, 255, 255))}]
@dispatcher.add_method
def SetLABValue(*lab_value):
    #print(lab_value)
    return runbymainth(lab_adjust.setLABValue, lab_value)

# save color threshold
@dispatcher.add_method
def GetLABValue():
    return (True, lab_adjust.getLABValue()[1], 'GetLABValue')

# save color threshold
@dispatcher.add_method
def SaveLABValue(color=''):
    return runbymainth(lab_adjust.saveLABValue, (color, ))

@dispatcher.add_method
def HaveLABAdjust():
    return (True, True, 'HaveLABAdjust')

@Request.application
def application(request):
    dispatcher["echo"] = lambda s: s
    dispatcher["add"] = lambda a, b: a + b
    response = JSONRPCResponseManager.handle(request.data, dispatcher)

    return Response(response.json, mimetype='application/json')

def startRPCServer():
    run_simple('', 9030, application)

if __name__ == '__main__':
    startRPCServer()
