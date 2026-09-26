"""
FitBuddy - AI Fitness Plan Generator
FastAPI entry point (Milestone 2, Activity 2.2).

Responsibilities:
- Load environment variables (GOOGLE_API_KEY) from .env
- Create the database tables on startup
- Mount the /static folder (background image, assets)
- Include all route handlers from routes.py
"""

import os

from dotenv import load_dotenv

# Load .env before any module that reads GOOGLE_API_KEY is imported
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routes import router

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(
    title="FitBuddy - AI Fitness Plan Generator",
    description="Generate personalized 7-day workout plans and nutrition tips using Google Gemini.",
    version="1.0.0",
)

# Create tables in fitbuddy.db (auto-creates the SQLite file on first run)
init_db()

# Serve static files such as /static/images/gym-bg.jpg
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Register all HTML + JSON API routes
app.include_router(router)
