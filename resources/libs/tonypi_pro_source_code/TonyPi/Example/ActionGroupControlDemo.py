import time
import threading
import hiwonder.ActionGroupControl as AGC

print('''
**********************************************************
*********Function: Hiwonder TonyPi expansion board, action group control routine********
**********************************************************
----------------------------------------------------------
Official website:http://www.hiwonder.com
Online mall:https://huaner.tmall.com/
----------------------------------------------------------
The following commands need be opened in LX terminal by press "ctrl+alt+t" or clicking black LX terminal icon.
----------------------------------------------------------
Usage:
    python3 ActionGroupControlDemo.py
----------------------------------------------------------
Version: --V1.2  2021/07/03
----------------------------------------------------------
Tips:
 * Press "Ctrl+C" close the running program, if fail to close, please try several times!
----------------------------------------------------------
''')

# Action groups need to be tored in the path /home/pi/TonyPi/ActionGroups.
AGC.runActionGroup('stand')  # The parameter is action group name without the suffix and inputted in the form of character.
AGC.runActionGroup('go_forward', times=2, with_stand=True)  # The seconad parameter is the runing times of action and it is 1 by default. 0 represents circularly running. The third parameter represents whether to end up with step posture

threading.Thread(target=AGC.runActionGroup, args=('go_forward', 0, True)).start()  # The blocking  action running function needs to be started by subthread if want to loop this function and stop after a period of time.
time.sleep(3)
AGC.stopActionGroup()  # stop after moving forward for 3 seconds.