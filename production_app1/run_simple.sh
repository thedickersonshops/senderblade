#!/bin/bash

# Kill any existing Python processes on ports 5001 and 8000
echo "Stopping any existing servers..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Install required packages
echo "Installing required packages..."
pip install flask flask-cors requests

# Start the backend server
echo "Starting backend server..."
python simple_fix.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 2

# Start the frontend server
echo "Starting frontend server..."
python -m http.server 8000 &
FRONTEND_PID=$!

# Function to handle script termination
function cleanup {
  echo "Stopping servers..."
  kill $BACKEND_PID
  kill $FRONTEND_PID
  exit
}

# Set up trap to catch Ctrl+C
trap cleanup INT

echo ""
echo "==================================================="
echo "SIMPLE EMAIL SENDER IS RUNNING"
echo "==================================================="
echo "Frontend: http://localhost:8000/simple.html"
echo "Backend: http://localhost:5001/api"
echo ""
echo "FEATURES:"
echo "- Real SMTP validation that actually tests connections"
echo "- Real proxy validation that actually tests connections"
echo "- Working upload functionality"
echo "- Simple, direct approach like email verifier"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "==================================================="

# Wait for user to press Ctrl+C
wait