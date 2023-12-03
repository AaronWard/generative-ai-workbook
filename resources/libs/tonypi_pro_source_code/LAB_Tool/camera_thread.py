#!/usr/bin/env python3
# encoding: utf-8
# Date:2021/10/25
# Author:aiden
import cv2
import time
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

class OpenCV_Camera(QThread):
    raw_data = pyqtSignal(np.ndarray)

    def __init__(self, port):
        super(OpenCV_Camera, self).__init__()
        
        self.port = port
        self.running = False
        self.camera = None 

    def open(self):
        self.camera = cv2.VideoCapture(self.port)
        self.running = True
    
    def close(self):
        self.running = False
        time.sleep(0.2)
        if self.camera is not None:
            self.camera.release()
    
    def run(self):
        while self.running:
            ret, image = self.camera.read()
            if ret:
                self.raw_data.emit(image)
                time.sleep(0.01)
