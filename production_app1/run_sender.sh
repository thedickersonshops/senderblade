#!/bin/bash

# Kill any existing Python processes on ports 5001 and 8000
echo "Stopping any existing servers..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Copy files
echo "Setting up sender app..."
cp backend/lists_api_simple.py backend/lists_api.py
cp static/index_sender.html static/index.html

# Start the backend server
echo "Starting backend server..."
cd backend
python app_sender.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 2

# Start the frontend server
echo "Starting frontend server..."
cd ../static
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
echo "EMAIL SENDER APP IS RUNNING"
echo "==================================================="
echo "Frontend: http://localhost:8000"
echo "Backend: http://localhost:5001/api"
echo ""
echo "FEATURES:"
echo "- Simplified app focused on sending emails"
echo "- Lists with pagination for contacts"
echo "- SMTP server management with validation"
echo "- Proxy management with validation"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "==================================================="

# Wait for user to press Ctrl+C
wait