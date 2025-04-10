from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from AI import Layer_Dense, Activation_ReLU, AI
from PIL import Image
import numpy as np
import uvicorn
import json
import io

app = FastAPI()
dense1 = Layer_Dense(784, 128)
dense2 = Layer_Dense(128, 10)
a1 = Activation_ReLU()

@app.get("/")
async def root():
    return {"message": "J3K Klang", "status": "ok"}

@app.post("/predict")
async def classify(file: UploadFile = File(...)):
    try:
        # Read and preprocess image
        image = Image.open(io.BytesIO(await file.read())).convert("L").resize((28, 28))
        prediction = AI(image, dense1, dense2, a1)
        return JSONResponse(content={"prediction": prediction})
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == '__main__':
    uvicorn.run("backend:app", host="0.0.0.0", port=8305, reload=True)