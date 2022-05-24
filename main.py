import numpy as np
import cv2
import sys
import time

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model

import serial.tools.list_ports


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        loadUi('UI/main.ui', self)
        self.UI_component_init()
        self.connect_buttons()
        self.update_ports()
        self.src_flag = None

    def UI_component_init(self):
        self.setFixedSize(545, 795)
        self.lbl_status.setText('')
        self.lbl_status.setStyleSheet("background-color: gray")
        self.setWindowIcon(QIcon("UI/icons/bottle.png"))
        self.setWindowTitle("Glass Bottle Defect Detection")
        self.btn_refresh.setIcon(QIcon("UI/icons/refresh.png"))
        self.model = load_model("model/defects_detector.model")
        self.classes = ["broken", "good"]

    def connect_buttons(self):
        self.btn_start.clicked.connect(self.call_model)
        self.btn_select_img.clicked.connect(self.select_img)
        self.btn_connect2Ard.clicked.connect(self.connect_arduino)
        self.btn_refresh.clicked.connect(self.update_ports)

    def connect_arduino(self):
        port = self.device_combo.currentText()
        try:
            self.arduino = serial.Serial(port=port, baudrate=115200, timeout=.1)
            self.lbl_ard_status.setStyleSheet("background-color: rgb(90, 255, 129)")
        except:
            pass



    def update_ports(self):
        comlist = serial.tools.list_ports.comports()
        for element in comlist:
            self.device_combo.addItem(element.name)


    def select_img(self):
        self.img_url = QFileDialog.getOpenFileName(self, caption='Select a video')[0]
        self.src_flag = 1

    def call_model(self):
        try:
            self.arduino.write(bytes(str(1), 'utf-8'))
            time.sleep(0.05)
        except:
            self.lbl_start_status.setText("Arduino isn't connected")
            pass

        #Select source
        if self.src_flag == 1: #process image
            img_org = cv2.imread(self.img_url)
            ret = 1
            self.src_flag = 0
        else:
            cam_ip = self.te_ip.toPlainText()
            if cam_ip == '0' or cam_ip.startswith('rtsp') or cam_ip.startswith('http') or cam_ip.endswith('.txt'):
                #convert webcam to string
                if cam_ip == '0':
                    cam_ip = 0


                self.lbl_start_status.setText("Livecam connected")
                self.lbl_start_status.setStyleSheet("color: white")

                vid_cap = cv2.VideoCapture(cam_ip)
                #to make sure we have a frame
                while True:
                    ret, img_org = vid_cap.read()
                    if ret:
                        break

            else:
                self.lbl_start_status.setText("Invalid Livecam")
                self.lbl_start_status.setStyleSheet("color: red")
        if ret :
            img_org = cv2.cvtColor(img_org, cv2.COLOR_BGR2RGB)

            img = cv2.resize(img_org, (224, 224), interpolation=cv2.INTER_AREA)
            res = self.detect_image(img)
            cls = self.classes[np.argmax(res)]
            conf = f'{res[0][np.argmax(res)]:.2f}'

            img_org = cv2.resize(img_org, (310, 720), interpolation=cv2.INTER_AREA)

            if cls == 'broken':
                self.lbl_status.setText('Broken Bottle')
                self.lbl_status.setStyleSheet("background-color: rgb(255, 78, 78)")


            elif cls == 'good':
                self.lbl_status.setText('Good Bottle')
                self.lbl_status.setStyleSheet("background-color: rgb(90, 255, 129)")

            h, w, c = img_org.shape
            img_vis = QImage(img_org.data, w, h, c * w, QImage.Format_RGB888)

            self.image_space.setPixmap(QPixmap.fromImage(img_vis))


    def detect_image(self,img):
        img = img_to_array(img)
        img = preprocess_input(img)
        img = img.reshape(1,img.shape[0],img.shape[1],3)
        pred = self.model.predict(img)
        return pred


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()