from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import numpy as np
from model import Model
import uvicorn
import json
import io

app = FastAPI()
model = Model()

@app.get("/")
async def root():
    return {"message": "J3K Klang", "status": "ok"}

@app.post("/predict")
async def classify(file: UploadFile = File(...)):
    try:
        # Read and preprocess image
        image = Image.open(io.BytesIO(await file.read())).convert("L").resize((64, 64))
        prediction = model.run(image)
        return JSONResponse(content={"prediction": prediction})
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == '__main__':
    uvicorn.run("backend:app", host="0.0.0.0", port=8305, reload=True)