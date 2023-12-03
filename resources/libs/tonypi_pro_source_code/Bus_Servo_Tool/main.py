#!/usr/bin/env python3
# encoding: utf-8
import time
from ServoCmd import *
from Ui import Ui_Form
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class MainWindow(QWidget, Ui_Form):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        #################################界面#######################################
        self.id = 0
        self.dev = 0
        self.servoTemp = 0
        self.servoMin = 0
        self.servoMax = 0
        self.servoMinV = 0
        self.servoMaxV = 0
        self.servoMove = 0
        self.horizontalSlider_servoTemp.valueChanged.connect(lambda: self.horizontalSlider_valuechange('servoTemp'))
        self.horizontalSlider_servoMin.valueChanged.connect(lambda: self.horizontalSlider_valuechange('servoMin'))
        self.horizontalSlider_servoMax.valueChanged.connect(lambda: self.horizontalSlider_valuechange('servoMax'))
        self.horizontalSlider_servoMinV.valueChanged.connect(lambda: self.horizontalSlider_valuechange('servoMinV'))
        self.horizontalSlider_servoMaxV.valueChanged.connect(lambda: self.horizontalSlider_valuechange('servoMaxV'))
        self.horizontalSlider_servoMove.valueChanged.connect(lambda: self.horizontalSlider_valuechange('servoMove'))

        self.pushButton_read.pressed.connect(lambda: self.button_clicked('read'))
        self.pushButton_set.pressed.connect(lambda: self.button_clicked('set'))
        self.pushButton_default.pressed.connect(lambda: self.button_clicked('default'))
        self.pushButton_resetPos.pressed.connect(lambda: self.button_clicked('resetPos'))
        
        self.validator2 = QIntValidator(-125, 125)
        self.lineEdit_servoDev.setValidator(self.validator2)
        
        self.readOrNot = False
        
    # 弹窗提示函数
    def message_from(self, str):
        try:
            QMessageBox.about(self, '', str)
        except:
            pass

    # 窗口退出
    def closeEvent(self, e):        
        result = QMessageBox.question(self,
                                    "Prompt box",
                                    "quit?",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
        if result == QMessageBox.Yes:
            QWidget.closeEvent(self, e)
        else:
            e.ignore()
    ################################################################################################
    def horizontalSlider_valuechange(self, name):
        if name == 'servoTemp':
            self.temp = str(self.horizontalSlider_servoTemp.value())
            self.label_servoTemp.setText(self.temp + '℃')
        if name == 'servoMin':
            self.servoMin = str(self.horizontalSlider_servoMin.value())
            self.label_servoMin.setText(self.servoMin)
        if name == 'servoMax':
            self.servoMax = str(self.horizontalSlider_servoMax.value())
            self.label_servoMax.setText(self.servoMax)
        if name == 'servoMinV':
            self.servoMinV = str(self.horizontalSlider_servoMinV.value()/10)
            self.label_servoMinV.setText(self.servoMinV + 'V')
        if name == 'servoMaxV':
            self.servoMaxV = str(self.horizontalSlider_servoMaxV.value()/10)
            self.label_servoMaxV.setText(self.servoMaxV + 'V')
        if name == 'servoMove':
            self.servoMove = str(self.horizontalSlider_servoMove.value())            
            self.label_servoMove.setText(self.servoMove)
            setBusServoPulse(self.id, int(self.servoMove), 0)
    
    def button_clicked(self, name):
        if name == 'read':
            try:
                self.id = getServoID()
                if self.id is None:
                    self.message_from('read id failed!!')
                    return
                self.readOrNot = True
                
                self.dev = getServoDeviation(self.id)
                if self.dev > 125:
                    self.dev = -(0xff-(self.dev - 1))
                    
                self.servoTemp = getServoTempLimit(self.id)
                (self.servoMin, self.servoMax) = getServoAngleLimit(self.id)
                (self.servoMinV, self.servoMaxV) = getServoVinLimit(self.id)
                self.servoMove = getServoPulse(self.id)
                
                currentVin = getServoVin(self.id)

                currentTemp = getServoTemp(self.id)

                self.lineEdit_servoID.setText(str(self.id))
                self.lineEdit_servoDev.setText(str(self.dev))
                
                self.horizontalSlider_servoTemp.setValue(self.servoTemp)
                self.horizontalSlider_servoMin.setValue(self.servoMin)
                self.horizontalSlider_servoMax.setValue(self.servoMax)
                MinV = self.servoMinV
                MaxV = self.servoMaxV            
                self.horizontalSlider_servoMinV.setValue(int(MinV/100))
                self.horizontalSlider_servoMaxV.setValue(int(MaxV/100))

                self.label_servoCurrentP.setText(str(self.servoMove))
                self.label_servoCurrentV.setText(str(round(currentVin/1000.0, 2)) + 'V')
                self.label_servoCurrentTemp.setText(str(currentTemp) + '℃')

                self.horizontalSlider_servoMove.setValue(self.servoMove)
            except BaseException as e:
                self.message_from('unknown error!')
                print(e)
                return
            
            self.message_from('success')
            
        elif name == 'set':
            if self.readOrNot is False:
                self.message_from('please read first！')
                return
            id = self.lineEdit_servoID.text()
            if id == '':
                self.message_from('error: id is None')
                return           
            dev = self.lineEdit_servoDev.text()
            if dev is '':
                dev = 0
            dev = int(dev)
            if dev > 125 or dev < -125:
                self.message_from('error: dev range error')
                return          
            temp = self.horizontalSlider_servoTemp.value()
            pos_min = self.horizontalSlider_servoMin.value()
            pos_max = self.horizontalSlider_servoMax.value()
            if pos_min > pos_max:
                self.message_from('error: pulse range error')
                return
            vin_min = self.horizontalSlider_servoMinV.value()
            vin_max = self.horizontalSlider_servoMaxV.value()
            if vin_min > vin_max:
                self.message_from('error: voltage range error')
                return
            pos = self.horizontalSlider_servoMove.value()
            
            id = int(id)
            
            try:
                setServoID(self.id, id)
                time.sleep(0.01)
                if getServoID() != id:
                    self.message_from('set id failed！')
                    return
                setServoDeviation(id, dev)
                time.sleep(0.01)
                saveServoDeviation(id)
                time.sleep(0.01)
                d = getServoDeviation(id)
                if d > 125:
                    d = -(0xff-(d - 1))               
                if d != dev:
                    self.message_from('set dev failed！')
                    return            
                setServoMaxTemp(id, temp)
                time.sleep(0.01)
                if getServoTempLimit(id) != temp:
                    self.message_from('set temp failed！')
                    return 
                setServoAngleLimit(id, pos_min, pos_max)
                time.sleep(0.01)
                if getServoAngleLimit(id) != (pos_min, pos_max):
                    self.message_from('set pulse failed！')
                    return 
                setServoVinLimit(id, vin_min*100, vin_max*100)
                time.sleep(0.01)
                if getServoVinLimit(id) != (vin_min*100, vin_max*100):
                    self.message_from('set voltage failed！')
                    return 
                setServoPulse(id, pos, 0)
            except BaseException as e:
                self.message_from('unknown error!')
                print(e)
                return                
            
            self.message_from('success')
            
        elif name == 'default':
            if self.readOrNot is False:
                self.message_from('please read first！')
                return
            try:
                setServoID(self.id, 1)
                time.sleep(0.01)
                if getServoID() != 1:
                    self.message_from('set id failed！')
                    return
                setServoDeviation(1, 0)
                time.sleep(0.01)
                saveServoDeviation(1)
                time.sleep(0.01)
                if getServoDeviation(1) != 0:
                    self.message_from('set dev failed！')
                    return
                setServoMaxTemp(1, 85)
                time.sleep(0.01)
                if getServoTempLimit(1) != 85:
                    self.message_from('set temp failed！')
                    return
                setServoAngleLimit(1, 0, 1000)
                time.sleep(0.01)
                if getServoAngleLimit(1) != (0, 1000):
                    self.message_from('set pulse failed！')
                    return          
                setServoVinLimit(1, 4500, 14000)
                time.sleep(0.01)
                if getServoVinLimit(1) != (4500, 14000):
                    self.message_from('set voltage failed！')
                    return             
                setServoPulse(1, 500, 0)
            except BaseException as e:
                self.message_from('unknown error!')
                print(e)
                return
            self.message_from('success')
        elif name == 'resetPos':
            self.horizontalSlider_servoMove.setValue(500)
            setServoPulse(self.id, 500, 0)

if __name__ == "__main__":  
    app = QApplication(sys.argv)
    myshow = MainWindow()
    myshow.show()
    sys.exit(app.exec_())