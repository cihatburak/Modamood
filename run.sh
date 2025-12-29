#!/bin/bash

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your HF_API_KEY!"
fi

# Kill any existing processes on ports 8000 or 8501
pkill -f "uvicorn backend.main:app"
pkill -f "streamlit run"

# Activate virtual environment
source .venv/bin/activate

echo "Starting Backend..."
.venv/bin/uvicorn backend.main:app --reload > backend.log 2>&1 &
BACKEND_PID=$!

echo "Waiting for Backend to initialize..."
sleep 5

echo "Starting Frontend..."
.venv/bin/streamlit run frontend/app.py &
FRONTEND_PID=$!

echo "ModaMood is running!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Press CTRL+C to stop."

wait
