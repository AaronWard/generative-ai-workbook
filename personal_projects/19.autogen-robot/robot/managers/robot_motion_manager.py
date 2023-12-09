"""
This script is a manager object for interacting
with a the rasberry pi controlling the robot.

Written by: Aaron Ward - 3rd December 2023
"""
import os
import sys
import paramiko
import threading
# from dotenv import load_dotenv
from dotenv import find_dotenv, load_dotenv

# from hiwonder.Board import *
# import hiwonder.ActionGroupControl as AGC

class RobotMotionManager:
    def __init__(self, **kwargs):
        self._model = kwargs.get('model', "gpt-4-1106-preview")
        self._env = kwargs.get('env', "../../../.env")
        
        load_dotenv(find_dotenv(filename=self._env))

        self.hostname = os.getenv('RASPBERRY_PI_IP')
        self.port = int(os.getenv('RASPBERRY_PI_PORT'))
        self.username = os.getenv('RASPBERRY_PI_USERNAME')
        self.password = os.getenv('RASPBERRY_PI_PASSWORD')

        # print("Hostname:", self.hostname)
        # print("Port:", self.port)
        # print("Username:", self.username)
        # print("Password:", self.password)

    def send_action(self, command):
        """
        Send terminal command to raspberry pi
        """
        command = f"cd /home/pi/github/tonypi-sdk/src/tonypisdk/controls && python3 action_group_controller.py {command}"
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Connect to the Raspberry Pi
            client.connect(
                hostname=self.hostname, 
                username=self.username,
                password=self.password, 
                port=self.port
            )

            # Execute the command
            _, stdout, stderr = client.exec_command(command)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')

            if error:
                print("Error:", error)
            if output:
                print("Output:", output)
                return output
        finally:
            client.close()
            return None

if __name__ == "__main__":
    rmm = RobotMotionManager()
    rmm.send_action(command="cd /home/pi/TonyPi/HiwonderSDK/hiwonder/ && python3 ActionGroupControl.py kneel_down")