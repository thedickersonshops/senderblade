#!/bin/bash

# Kill any existing Python processes on ports 5001 and 8000
echo "Stopping any existing servers..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Copy fixed files
echo "Copying fixed files..."
cp static/index_fixed.html static/index.html
cp static/js/smtp_test_fix.js static/js/smtp.js
cp static/js/proxy_test_fix.js static/js/proxies.js
cp static/js/api_test_fix.js static/js/api.js

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
echo "FIXED APPLICATION WITH TEST FIX IS RUNNING"
echo "==================================================="
echo "Frontend: http://localhost:8000"
echo "Backend: http://localhost:5001/api"
echo ""
echo "FIXED ISSUES:"
echo "- Upload button works correctly"
echo "- SMTP testing works for existing servers"
echo "- Proxy testing works for existing proxies"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "==================================================="

# Wait for user to press Ctrl+C
wait