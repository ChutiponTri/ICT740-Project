from PyQt6.QtCore import QThread, pyqtSignal
import requests

class API(QThread):
    signal = pyqtSignal(object)
    def __init__(self, image):
        super().__init__()
        self.image = image

    def run(self):
        url = "http://localhost:8305/predict"
        
        # Sending image to backend using in-memory byte data
        files = {"file": ("drawing.png", self.image, "image/png")}
        response = requests.post(url, files=files)

        self.signal.emit(response.json())
