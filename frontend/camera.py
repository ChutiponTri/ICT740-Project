from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QImage, QPixmap, QFont,QIcon
from io import BytesIO
from PIL import Image
from api import API
import time
import cv2
import os

font = QFont("Arial", 14)
script_dir = os.path.dirname(os.path.abspath(__file__))

class CameraWindow(QMainWindow):
    signal = pyqtSignal()
    def __init__(self, index):
        super().__init__()
        self.setWindowTitle("Camera Feed")
        self.setGeometry(100, 100, 800, 600)
        window_icon = os.path.join(script_dir, "icons", "kitty.png")
        self.setWindowIcon(QIcon(window_icon))    
        
        try:
            index = int(index)
        except ValueError:
            index = 0

        # Central widget and layout
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        # Create Buttons
        clear_button = QPushButton("Clear")
        predict_button = QPushButton("Predict")
        self.result = QLabel("Press Predict Button to See Result")
        self.videoLabel = QLabel("")

        # Setting Button Font
        clear_button.setFont(font)
        predict_button.setFont(font)
        self.result.setFont(font)

        # Button Style
        clear_button.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50; /* Green */
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
        }
        QPushButton:hover {
            background-color: #45a049; /* Darker green */
        }
        """)
        predict_button.setStyleSheet("""
            QPushButton {
                background-color: #008CBA; /* Blue */
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #007bb5; /* Darker blue */
            }
        """)

        # Setting Video Label
        self.videoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.videoLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.videoLabel.setMinimumSize(self.size())

        # Button Functionalities
        clear_button.clicked.connect(self.clear_pred)
        predict_button.clicked.connect(self.predict)

        # Button Layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(predict_button)
        button_layout.addWidget(clear_button)
        button_layout.addStretch(1)

        # Predict Layout
        pred_layout = QHBoxLayout()
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
    def clear_pred(self):
        self.result.setText("Press Predict Button to See Result")
        self.cameraThread.reset()

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
            result = data["prediction"]
            result = ", ".join(result)
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
        self.flag = True

    def run(self):
        self.running = True
        cap = cv2.VideoCapture(self.camera_index)
        while self.running:
            ret, frame = cap.read()
            if ret:
                self.last_frame = frame
                if self.flag:
                    self.frameCaptured.emit(frame)
                time.sleep(0.033)  # ~30 FPS
            else:
                break
        cap.release()

    def stop(self):
        self.running = False

    def reset(self):
        self.flag = True

    def get_last_frame(self):
        self.flag = False
        return self.last_frame

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraWindow(0, "easy")
    window.show()
    sys.exit(app.exec())
