from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import tensorflow as tf
import numpy as np
from geopy.geocoders import Nominatim
import os

app = FastAPI()

# Load pre-trained CNN model
MODEL_PATH = "models/waste_classifier.h5"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
model = tf.keras.models.load_model(MODEL_PATH)

# Waste categories
CATEGORIES = ["Plastic", "Metal", "Paper", "Food", "Glass", "Other"]

# Geo-locator for finding recycling centers
geolocator = Nominatim(user_agent="smartwasteai")

@app.get("/")
def read_root():
    return {"message": "Welcome to SmartWasteAI Backend"}

@app.post("/classify/")
async def classify_waste(file: UploadFile):
    try:
        # Read image
        contents = await file.read()
        img = tf.image.decode_image(contents, channels=3)
        img = tf.image.resize(img, [224, 224])  # Resize to model's input size
        img = tf.expand_dims(img, axis=0) / 255.0  # Normalize

        # Predict category
        predictions = model.predict(img)
        predicted_class = CATEGORIES[np.argmax(predictions)]

        # Suggest disposal methods
        disposal_methods = {
            "Plastic": "Recycle at local plastic recycling centers or reuse creatively.",
            "Metal": "Recycle at metal collection points or scrap yards.",
            "Paper": "Recycle at paper recycling facilities or compost.",
            "Food": "Compost or use for animal feed.",
            "Glass": "Recycle at glass recycling facilities.",
            "Other": "Dispose of responsibly in non-recyclable waste bins."
        }

        return {
            "category": predicted_class,
            "confidence": float(np.max(predictions)),
            "suggestion": disposal_methods[predicted_class]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recycling-centers/")
def get_recycling_centers(latitude: float, longitude: float):
    """
    Find the nearest recycling centers based on geo-coordinates.
    Note: Replace with a proper database or API for real-world data.
    """
    location = geolocator.reverse((latitude, longitude))
    if location:
        return {
            "nearest_recycling_center": "Example Recycling Center (2 km away)",
            "address": location.address
        }
    return {"error": "Unable to fetch recycling centers. Please try again later."}
