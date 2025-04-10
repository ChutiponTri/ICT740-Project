from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PyQt6.QtGui import QIcon, QImage, QPainter, QAction , QPen, QFont
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from equation import Equation
from api import API
from io import BytesIO
from PIL import Image
import sys

font = QFont("Cordia New", 16)

class DrawingWindow(QMainWindow):
    signal = pyqtSignal()
    def __init__(self, mode):
        super().__init__()
        # Create Window
        self.setWindowTitle("Paint")
        self.setWindowIcon(QIcon("icons/Tifa.jpg"))
        self.setGeometry(300, 200, 600, 600)
        self.mode = mode

        # Create Buttons
        random_button = QPushButton("Random")
        predict_button = QPushButton("Predict")
        self.equation = QLabel("Equation: Unknown")
        self.result = QLabel("")

        # Setting Button Font
        random_button.setFont(font)
        predict_button.setFont(font)
        self.equation.setFont(font)
        self.result.setFont(font)

        # Button Functionalities
        random_button.clicked.connect(self.random_equation)
        predict_button.clicked.connect(self.predict)

        # Create Actions
        save_action = QAction(QIcon("icons/Dummy.jpg"), "Save", self)
        clear_action = QAction(QIcon("icons/Logo.jpg"), "Clear", self)
        exit_action = QAction(QIcon("icons/Tifa.jpg"), "Exit", self)
        exit_action.triggered.connect(self.close)
        brush_3 = QAction("3px", self)
        brush_5 = QAction("5px", self)
        brush_7 = QAction("7px", self)
        brush_9 = QAction("9px", self)
        black = QAction("Black", self)
        white = QAction("White", self)
        red = QAction("Red", self)
        green = QAction("Green", self)
        yellow = QAction("Yellow", self)
        pen = QAction("Pen", self)
        erase = QAction("Eraser", self)

        # Create Menubar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        sz_menu = menubar.addMenu("Brush Size")
        color_menu = menubar.addMenu("Brush Color")
        select_menu = menubar.addMenu("Select")

        # Add Actions to Menubar
        file_menu.addAction(save_action)
        file_menu.addAction(clear_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        sz_menu.addAction(brush_3)
        sz_menu.addAction(brush_5)
        sz_menu.addAction(brush_7)
        sz_menu.addAction(brush_9)
        color_menu.addAction(black)
        color_menu.addAction(white)
        color_menu.addAction(red)
        color_menu.addAction(green)
        color_menu.addAction(yellow)
        select_menu.addAction(pen)
        select_menu.addAction(erase)

        # Create White image
        self.image = QImage(self.size(), QImage.Format.Format_RGB32)
        self.image.fill(Qt.GlobalColor.white)

        # Set Initial Condition
        self.drawing = False
        self.is_pen = True
        self.BrushSize = 5
        self.BrushColor = Qt.GlobalColor.black
        self.LastPoint = QPoint()

        # Action Connect 
        save_action.triggered.connect(self.save)
        clear_action.triggered.connect(self.clear)
        brush_3.triggered.connect(self.brush_3)
        brush_5.triggered.connect(self.brush_5)
        brush_7.triggered.connect(self.brush_7)
        brush_9.triggered.connect(self.brush_9)
        black.triggered.connect(self.black)
        white.triggered.connect(self.white)
        red.triggered.connect(self.red)
        green.triggered.connect(self.green)
        yellow.triggered.connect(self.yellow)
        pen.triggered.connect(self.toggle_pen)
        erase.triggered.connect(self.toggle_erase)

        # Button Layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(random_button)
        button_layout.addWidget(predict_button)
        button_layout.addStretch(1)

        # Predict Layout
        pred_layout = QHBoxLayout()
        pred_layout.addWidget(self.equation)
        pred_layout.addWidget(self.result)

        # Layout
        layout = QVBoxLayout()
        layout.addLayout(button_layout)
        layout.addLayout(pred_layout)
        layout.addStretch(1)

        # Create a container widget to hold the layout
        container = QWidget()
        container.setLayout(layout)

        # Set container as central widget
        self.setCentralWidget(container)

    # Function to Generate Random Equation
    def random_equation(self):
        equation = Equation.random(self.mode)
        self.equation.setText(equation)
        self.result.setText("")
        self.clear()

    # Function to Request API Prediction
    def predict(self):
        # Convert the QImage to a Pillow Image (in memory)
        image_pil = Image.fromqpixmap(self.image)
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

    # Function for Mouse Press Event
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.LastPoint = event.position()
            print(self.LastPoint)

    # Function for Mouse Move Event
    def mouseMoveEvent(self , event):
        if (event.buttons() & Qt.MouseButton.LeftButton):
            painter = QPainter(self.image)
            if self.is_pen:
                painter.setPen(QPen(self.BrushColor, self.BrushSize, Qt.PenStyle.SolidLine))
                painter.drawLine(self.LastPoint, event.position())
            else:  # Erase mode
                painter.setPen(QPen(Qt.GlobalColor.white, self.BrushSize, Qt.PenStyle.SolidLine))
                painter.drawLine(self.LastPoint, event.position())
            self.LastPoint = event.position()
            self.update()
    
    # Function for Mouse Release Event
    def mouseReleaseEvent(self,event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    # Function for Paint Event
    def paintEvent(self, event):
        canvas_painter = QPainter(self)
        canvas_painter.drawImage(self.rect(), self.image, self.image.rect())

    # Function to Save Image
    def save(self):
        file_path, _ = QFileDialog.getSaveFileName(self , "Save image " , "" , "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*)")
        if file_path == "":
            return self.image.save(file_path)

    # Function to Clear the Screen
    def clear(self):
        self.image.fill(Qt.GlobalColor.white)
        self.update()

    # Function to Toggle Brush Size: 3
    def brush_3(self):
        self.BrushSize = 3
        print(self.BrushSize, "px")
    
    # Function to Toggle Brush Size: 5
    def brush_5(self):
        self.BrushSize = 5
        print(self.BrushSize, "px")
    
    # Function to Toggle Brush Size: 7
    def brush_7(self):
        self.BrushSize = 7
        print(self.BrushSize, "px")
    
    # Function to Toggle Brush Size: 9
    def brush_9(self):
        self.BrushSize = 9
        print(self.BrushSize, "px")

    # Function to Toggle Brush Color: Black
    def black(self):
        self.BrushColor = Qt.GlobalColor.black
        print(str(self.BrushColor).split(".")[1])

    # Function to Toggle Brush Color: White
    def white(self):
        self.BrushColor = Qt.GlobalColor.white
        print(str(self.BrushColor).split(".")[1])
    
    # Function to Toggle Brush Color: Red
    def red(self):
        self.BrushColor = Qt.GlobalColor.red
        print(str(self.BrushColor).split(".")[1])

    # Function to Toggle Brush Color: Green
    def green(self):
        self.BrushColor = Qt.GlobalColor.green
        print(str(self.BrushColor).split(".")[1])
    
    # Function to Toggle Brush Color: Yellow
    def yellow(self):
        self.BrushColor = Qt.GlobalColor.yellow
        print(str(self.BrushColor).split(".")[1])

    # Function to Toggle Mode: Pen
    def toggle_pen(self):
        self.is_pen = True  # Set to pen mode
        print("Pen mode")

    # Function to Toggle Mode: Eraser
    def toggle_erase(self):
        self.is_pen = False  # Set to eraser mode
        print("Eraser mode")

    # Function to Handle Close Event
    def closeEvent(self, event):
        self.signal.emit()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DrawingWindow("hard")
    window.show()
    sys.exit(app.exec())
