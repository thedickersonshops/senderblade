#!/bin/bash

# Kill any existing Python processes on ports 5001 and 8000
echo "Stopping any existing servers..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start the backend server
echo "Starting backend server..."
cd backend
python app_fixed.py &
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
echo "APPLICATION RESTARTED WITH VALIDATION FIXES"
echo "==================================================="
echo "Frontend: http://localhost:8000"
echo "Backend: http://localhost:5001/api"
echo ""
echo "FIXED ISSUES:"
echo "- SMTP validation now properly checks credentials"
echo "- Proxy validation now properly checks host and port"
echo "- All existing functionality preserved"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "==================================================="

# Wait for user to press Ctrl+C
wait