import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from backend.api import endpoints

# Load environment variables
load_dotenv()

app = FastAPI(title="ModaMood API", version="0.1.0")

# CORS Setup
origins = [
    "http://localhost",
    "http://localhost:8501", # Streamlit default port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(endpoints.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to ModaMood API"}
