from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QImage, QPixmap, QFont
from equation import Equation
from io import BytesIO
from PIL import Image
from api import API
import time
import cv2
import sys

font = QFont("Cordia New", 16)

class CameraWindow(QMainWindow):
    signal = pyqtSignal()
    def __init__(self, index, mode):
        super().__init__()
        self.setWindowTitle("Camera Feed")
        self.setGeometry(100, 100, 800, 600)
        try:
            index = int(index)
        except ValueError:
            index = 0
        self.mode = mode

        # Central widget and layout
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        # Create Buttons
        random_button = QPushButton("Random")
        predict_button = QPushButton("Predict")
        self.equation = QLabel("Equation: Unknown")
        self.result = QLabel("")
        self.videoLabel = QLabel("")

        # Setting Button Font
        random_button.setFont(font)
        predict_button.setFont(font)
        self.equation.setFont(font)
        self.result.setFont(font)

        # Setting Video Label
        self.videoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.videoLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.videoLabel.setMinimumSize(self.size())

        # Button Functionalities
        random_button.clicked.connect(self.random_equation)
        predict_button.clicked.connect(self.predict)

        # Button Layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(random_button)
        button_layout.addWidget(predict_button)
        button_layout.addStretch(1)

        # Predict Layout
        pred_layout = QHBoxLayout()
        pred_layout.addWidget(self.equation)
        pred_layout.addWidget(self.result)

        # QLabel for displaying video feed
        layout = QVBoxLayout()
        layout.addLayout(button_layout)
        layout.addLayout(pred_layout)
        layout.addStretch(1)
        layout.addWidget(self.videoLabel)
        layout.addStretch(1)

        centralWidget.setLayout(layout)

        # Initialize camera worker
        self.cameraThread = CameraThread(index)
        self.cameraThread.frameCaptured.connect(self.updateFrame)
        self.cameraThread.start()

    # Convert OpenCV frame to QImage and display in QLabel
    def updateFrame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(image)

        # Resize pixmap to fill the QLabel's size
        self.videoLabel.setPixmap(pixmap.scaled(self.videoLabel.size(), Qt.AspectRatioMode.KeepAspectRatio))

    # Function to Generate Random Equation
    def random_equation(self):
        equation = Equation.random(self.mode)
        self.equation.setText(equation)
        self.result.setText("")

    # Function to Request API Prediction
    def predict(self):
        frame = self.cameraThread.get_last_frame()
        if frame is not None:
            # Convert the QImage to a Pillow Image (in memory)
            image_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            image_pil = image_pil.resize((28, 28))
            
            # Save the Pillow image to an in-memory BytesIO buffer
            byte_io = BytesIO()
            image_pil.save(byte_io, format="PNG")
            byte_io.seek(0)  # Rewind the buffer to the beginning

            # Send the image data to the backend
            self.resp = API(byte_io)
            self.resp.signal.connect(self.update_label)
            self.resp.start()

    # Function to Update Label 
    def update_label(self, data):
        print(data)
        if "prediction" in data.keys():
            if "Unknown" not in self.equation.text():
                equation = self.equation.text()
                self.equation.setText(f"{equation} = {eval(equation)}")
            result = data["prediction"]
            self.result.setText(f"Prediction Result: {result}")

    # Ensure camera stops when the window is closed
    def closeEvent(self, event):
        self.cameraThread.stop()
        self.cameraThread.wait()
        self.signal.emit()

class CameraThread(QThread):
    frameCaptured = pyqtSignal(object)  # Emit frame data
    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self.running = False
        self.last_frame = None

    def run(self):
        self.running = True
        cap = cv2.VideoCapture(self.camera_index)
        while self.running:
            ret, frame = cap.read()
            if ret:
                self.last_frame = frame
                self.frameCaptured.emit(frame)
                time.sleep(0.033)  # ~30 FPS
            else:
                break
        cap.release()

    def stop(self):
        self.running = False

    def get_last_frame(self):
        return self.last_frame

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraWindow(0, "easy")
    window.show()
    sys.exit(app.exec())
