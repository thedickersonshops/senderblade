#!/bin/bash

# Kill any existing Python processes on ports 5001 and 8000
echo "Stopping any existing servers..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Update HTML to include direct fixes
echo "Updating HTML..."
sed -i.bak '/<\/body>/i \    <script src="js/direct_fixes.js"></script>' static/index.html

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
echo "DIRECT FIX FOR CRITICAL FUNCTIONALITY"
echo "==================================================="
echo "Frontend: http://localhost:8000"
echo "Backend: http://localhost:5001/api"
echo ""
echo "FIXED ISSUES:"
echo "- Upload button now works with direct event handler"
echo "- SMTP validation is stricter and more accurate"
echo "- Proxy validation is stricter and more accurate"
echo ""
echo "SMTP VALIDATION RULES:"
echo "- Gmail: smtp.gmail.com:587 with @gmail.com username"
echo "- Outlook: smtp.office365.com:587 with @outlook.com username"
echo "- Yahoo: smtp.mail.yahoo.com:587 with @yahoo.com username"
echo "- Password must be at least 8 characters"
echo ""
echo "PROXY VALIDATION RULES:"
echo "- HTTP proxies: ports 3128, 8080, 8118"
echo "- SOCKS5 proxies: ports 1080, 9050"
echo "- Valid IP address format required"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "==================================================="

# Wait for user to press Ctrl+C
wait