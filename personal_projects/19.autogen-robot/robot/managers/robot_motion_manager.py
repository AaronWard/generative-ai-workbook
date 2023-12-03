"""
This script is a manager object for interacting
with a the rasberry pi controlling the robot.

Written by: Aaron Ward - 3rd December 2023
"""
import os
import sys
import paramiko
import threading
from dotenv import load_dotenv

# from hiwonder.Board import *
# import hiwonder.ActionGroupControl as AGC

class RobotMotionManager:
    def __init__(self, **kwargs):
        self._model = kwargs.get('model', "gpt-4-1106-preview")
        self._env = kwargs.get('env', "../../../.env")
        load_dotenv(dotenv_path=self._env)

        self.hostname = os.getenv('RASPBERRY_PI_IP')
        self.port = os.getenv('RASPBERRY_PI_PORT')
        self.username = os.getenv('RASPBERRY_PI_USERNAME')
        self.password = os.getenv('RASPBERRY_PI_PASSWORD')

    def send_action(self, command):
        # Replace these variables with your Raspberry Pi's details
        command = 'ls'               # Command you want to execute

        # Create an SSH client instance
        client = paramiko.SSHClient()

        # Automatically add the Raspberry Pi's host key (this is not secure, see below)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Connect to the Raspberry Pi
            client.connect(self.hostname, username=self.username, password=self.password)

            # Execute the command
            stdin, stdout, stderr = client.exec_command(command)

            # Read the command output
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')

            if output:
                print("Output:", output)
            if error:
                print("Error:", error)

        finally:
            # Close the connection
            client.close()


if __name__ == "__main__":
    rmm = RobotMotionManager()
    rmm.send_action(command="ls")