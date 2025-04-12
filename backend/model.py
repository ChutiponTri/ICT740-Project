from tensorflow.keras.applications import MobileNet
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import categorical_crossentropy
from tensorflow.keras.applications.mobilenet import preprocess_input
from tensorflow.keras.metrics import categorical_accuracy, top_k_categorical_accuracy, categorical_crossentropy
import numpy as np
import cv2
import os

class Model():
    def __init__(self):
        # Set your variables
        size = 64
        NCATS = 340

        self.cats = self.list_all_categories()

        self.model = MobileNet(input_shape=(size, size, 1), alpha=1., weights=None, classes=NCATS)
        self.model.compile(optimizer=Adam(learning_rate=0.002), loss='categorical_crossentropy',
                    metrics=[categorical_crossentropy, categorical_accuracy, self.top_3_accuracy])

        # Load the saved weights
        self.model.load_weights("model/model.h5")

    # Function to Run Classification
    def run(self, image):
        # Path to your custom image
        img = self.prepare_custom_image(image)

        # Predict
        pred = self.model.predict(img)
        top3 = np.argsort(-pred[0])[:5]

        # Load category list and print top 5 predictions
        result = []
        for i in top3:
            result.append(self.cats[i])
            print(f"{i}: {self.cats[i]}")

        return result

    # Function to Return Top 3 Acc
    def top_3_accuracy(self, y_true, y_pred):
        return top_k_categorical_accuracy(y_true, y_pred, k=3)

    # Function to Prepare Image
    def prepare_custom_image(self, image, size=64):
        # Convert PIL Image to numpy array (grayscale)
        img = np.array(image)

        # Resize if needed (just to be sure)
        if img.shape != (size, size):
            img = cv2.resize(img, (size, size))

        # Invert image if background is white
        if img[0, 0] > 127:
            img = 255 - img

        img = img.astype(np.float32)
        img = np.expand_dims(img, axis=-1)  # Add channel dimension
        img = np.expand_dims(img, axis=0)   # Add batch dimension
        img = preprocess_input(img)

        return img

    # Function to Get All Categories
    def list_all_categories(self):
        INPUT_DIR = 'model/categories.txt'
        with open(INPUT_DIR, "r") as file:
            return sorted([line.strip() for line in file], key=str.lower)
        
if __name__ == '__main__':
    model = Model()
    model.run()

