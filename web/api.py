import streamlit as st
import requests

class API():
    @staticmethod
    def post(image, queue):
        url = "http://localhost:8305/predict"
        
        # Sending image to backend using in-memory byte data
        files = {"file": ("drawing.png", image, "image/png")}
        try:
            response = requests.post(url, files=files)
            result = response.json()
        except Exception as e:
            result = {"error": str(e)}
        queue.put(result)
