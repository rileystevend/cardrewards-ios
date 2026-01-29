import os

class Config:
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
    PLACES_RADIUS_METERS = int(os.getenv("PLACES_RADIUS_METERS", "35"))

    # Your backend (server/main.py) that calls OpenAI safely.
    RECOMMENDER_API_BASE_URL = os.getenv("RECOMMENDER_API_BASE_URL", "https://your-api.example.com")
