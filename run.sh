#!/bin/bash
# Start FastAPI backend in the background
echo "Starting FastAPI backend on port 8000..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to initialize
sleep 3

# Start Streamlit frontend
echo "Starting Streamlit frontend on port 8501..."
python -m streamlit run frontend/home.py --server.port 8501 --server.address 0.0.0.0

# When Streamlit exits, clean up backend
echo "Shutting down backend process (PID $BACKEND_PID)..."
kill $BACKEND_PID
