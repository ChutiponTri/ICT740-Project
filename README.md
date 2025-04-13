# ICT740-Project

This project demonstrates a hardware design for the ICT740 course, featuring both frontend and backend components for image classification.

## Project Structure

The project is organized into several folders and files:

### Frontend Folder
- **`api.py`**: Contains a class for making requests to the backend API, which is linked with the number recognition model.
- **`camera.py`**: Implements a camera window for capturing images, which are sent to the backend for classification.
- **`draw.py`**: Provides a window for drawing or writing numbers, which are then sent to the backend for classification.
- **`main.py`**: Main entry point for the UI, allowing the user to select modes and choose the camera.

### Backend Folder
- **`AI.py`**: Connects with the model to perform classification on the input data.
- **`model.py`** Connects with the model to perform classification of the input data.
- **`backend.py`**: Runs the FastAPI backend server, which handles classification requests.

### Web Folder
- **`api.py`**: Contains a class for making requests to the backend API, which is linked with the number recognition model.
- **`camera.py`**: Implements a camera page for capturing images, which are sent to the backend for classification.
- **`draw.py`**: Provides a page for drawing or writing numbers, which are then sent to the backend for classification.
- **`web.py`**: Main entry point for the Web UI, allowing the user to select modes and choose the camera.
- **`jek.jpg`**: An image to render at the welcome page.

### Model Folder
Contains the pre-trained model used for classification.

## Requirements

Make sure to install the required dependencies by running:
```bash
pip install -r requirements.txt
```

## Running the Project

### Frontend
To run the frontend, simply execute the `main.py` file:
```bash
python frontend/main.py
```

### Backend
To run the backend, make sure to navigate to the root directory of the project and then start the FastAPI server:
```bash
python backend/backend.py
```

## Notes
- The backend service must be run from the root directory to work correctly.
- The frontend uses camera capture and drawing windows, allowing the user to interact with the number recognition system.
