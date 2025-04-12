from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox, QHBoxLayout, QPushButton, QLabel, QMessageBox
from PyQt6.QtCore import pyqtSignal, QThread, Qt
from PyQt6.QtGui import QFont
from camera import CameraWindow
from draw import DrawingWindow
import cv2
import sys

font = QFont("Cordia New", 16)

class MainWindow(QMainWindow):
    max_cameras = 2
    avaiable = []
    flag = False
    def __init__(self):
        super().__init__()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.setWindowTitle("MainWindow")

        # Create Elements
        camera_label = QLabel("Please Select Camera")
        self.camera_box = QComboBox()
        mode_label = QLabel("Please Select Mode")
        self.mode_box = QComboBox()
        label_1 = QLabel("Welcome to our Program")
        label_2 = QLabel("Please Press Start when You are Ready")
        start = QPushButton("Start")

        # Set Elements Font
        label_1.setFont(QFont("Cordia New", 20, QFont.Weight.Bold))
        label_2.setFont(QFont("Cordia New", 20, QFont.Weight.Bold))
        mode_label.setFont(font)
        self.mode_box.setFont(font)
        camera_label.setFont(font)
        self.camera_box.setFont(font)
        start.setFont(font)

        # Create Camera Index Fetching Thread
        self.camera_thread = CameraThread(self.max_cameras)
        self.camera_thread.cameras_found.connect(self.update_camera_box)
        self.camera_thread.start()

        # Add Items to Mode 
        self.mode_box.addItems(["Select a Mode", "Camera", "Drawing"])

        # Set Button Functionalities
        start.clicked.connect(self.mode_playground)

        # Create Camera Selection Layout
        cam_layout = QHBoxLayout()
        cam_layout.addWidget(mode_label)
        cam_layout.addWidget(self.mode_box)
        cam_layout.addStretch(1)
        cam_layout.addWidget(camera_label)
        cam_layout.addWidget(self.camera_box)
        cam_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Create Box Layout
        layout = QVBoxLayout()
        layout.addLayout(cam_layout)
        layout.addStretch(1)
        layout.addWidget(label_1, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(label_2, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(start)
        layout.addStretch(2)

        # Set Window Layout
        central_widget.setLayout(layout)
        self.setGeometry(500, 100, 600, 600)

    # Function to Update Camera Index
    def update_camera_box(self, cameras: list):
        self.avaiable = cameras
        self.camera_box.addItems(cameras)
        self.flag = True

    # Function to Open Camera Playgroubd
    def mode_playground(self):
        self.check_mode_index()
        
    # Function to Check Mode Index
    def check_mode_index(self):
        if "Select" in self.mode_box.currentText():
            message = QMessageBox()
            message.setText("Please Select a Mode")
            message.setWindowTitle("Warning")
            message.setIcon(QMessageBox.Icon.Information)
            message.exec()
        elif self.mode_box.currentText() == "Camera":
            self.check_camera_index()
        else:
            self.check_for_drawing()

    # Function to Check for Camera Index
    def check_camera_index(self):
        if not self.flag:
            message = QMessageBox()
            message.setText("Warning: Camera Fetching is not yet Finish")
            message.setWindowTitle("Warning")
            message.setIcon(QMessageBox.Icon.Warning)
            message.exec()
        else:
            self.hide()
            self.camera_window = CameraWindow(self.camera_box.currentText())
            self.camera_window.signal.connect(self.show)
            self.camera_window.show()

    # Function to Check for Drawing
    def check_for_drawing(self):
        self.hide()
        self.draw = DrawingWindow()
        self.draw.signal.connect(self.show)
        self.draw.show()

class CameraThread(QThread):
    cameras_found = pyqtSignal(list)
    def __init__(self, max_cameras):
        super().__init__()
        self.max_cameras = max_cameras

    # Function to Fetch Camera Index
    def run(self):
        available = []
        for i in range(self.max_cameras):
            cap = cv2.VideoCapture(i)
            if cap.read()[0]:
                available.append(str(i))
                print(f"Camera index {i:02d} OK!")
                cap.release()
            else:
                print(f"Camera index {i:02d} not found...")
        self.cameras_found.emit(available)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())