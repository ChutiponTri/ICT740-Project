from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout
from PyQt6.QtGui import QImage, QPixmap
import cv2
import sys
import time

class CameraWorker(QThread):
    frameCaptured = pyqtSignal(object)  # Emit frame data

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self.running = False

    def run(self):
        self.running = True
        cap = cv2.VideoCapture(self.camera_index)
        while self.running:
            ret, frame = cap.read()
            if ret:
                self.frameCaptured.emit(frame)
                time.sleep(0.033)  # ~30 FPS
            else:
                break
        cap.release()

    def stop(self):
        self.running = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Camera Feed")
        self.setGeometry(100, 100, 800, 600)

        # Central widget and layout
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout()
        centralWidget.setLayout(layout)

        # QLabel for displaying video feed
        self.videoLabel = QLabel(self)
        self.videoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.videoLabel)

        # Initialize camera worker
        self.cameraWorker = CameraWorker()
        self.cameraWorker.frameCaptured.connect(self.updateFrame)
        self.cameraWorker.start()

    def updateFrame(self, frame):
        """ Convert OpenCV frame to QImage and display in QLabel """
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(image)

        # Resize pixmap to fit QLabel while maintaining aspect ratio
        self.videoLabel.setPixmap(pixmap.scaled(self.videoLabel.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def closeEvent(self, event):
        """ Ensure camera stops when the window is closed """
        self.cameraWorker.stop()
        self.cameraWorker.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
