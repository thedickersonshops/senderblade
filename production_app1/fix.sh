#!/bin/bash

# Kill any existing Python processes on ports 5001 and 8000
echo "Stopping any existing servers..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Update HTML to include direct fixes
echo "Updating HTML..."
cat > static/index.html << 'EOL'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Sender</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav id="sidebar" class="col-md-3 col-lg-2 d-md-block bg-dark sidebar collapse">
                <div class="position-sticky pt-3">
                    <div class="text-center mb-4">
                        <h3 class="text-white">Email Sender</h3>
                        <div class="text-muted" id="userInfo">User</div>
                    </div>
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link active" href="#" data-page="dashboard">
                                <i class="fas fa-tachometer-alt me-2"></i>
                                Dashboard
                            </a>
                        </li>
                        
                        <!-- Setup Section -->
                        <li class="nav-item mt-3">
                            <small class="text-muted px-3 d-block">SETUP</small>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" data-page="lists">
                                <i class="fas fa-list me-2"></i>
                                Lists
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" data-page="smtp">
                                <i class="fas fa-server me-2"></i>
                                SMTP Servers
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" data-page="proxies">
                                <i class="fas fa-shield-alt me-2"></i>
                                Proxies
                            </a>
                        </li>
                        
                        <!-- Campaigns Section -->
                        <li class="nav-item mt-3">
                            <small class="text-muted px-3 d-block">CAMPAIGNS</small>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" data-page="campaigns">
                                <i class="fas fa-paper-plane me-2"></i>
                                Campaigns
                            </a>
                        </li>
                    </ul>
                    <hr class="text-white">
                    <div class="px-3 mt-4">
                        <button id="logoutBtn" class="btn btn-outline-light w-100">
                            <i class="fas fa-sign-out-alt me-2"></i> Logout
                        </button>
                    </div>
                </div>
            </nav>

            <!-- Main content -->
            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4">
                <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                    <h1 id="pageTitle">Dashboard</h1>
                    <div class="btn-toolbar mb-2 mb-md-0">
                        <div class="btn-group me-2" id="pageActions">
                            <!-- Page-specific action buttons will be added here -->
                        </div>
                    </div>
                </div>

                <!-- Alert container -->
                <div id="alertContainer"></div>

                <!-- Page content -->
                <div id="pageContent">
                    <!-- Content will be loaded here -->
                </div>
            </main>
        </div>
    </div>

    <!-- Login Modal -->
    <div class="modal fade" id="loginModal" tabindex="-1" aria-labelledby="loginModalLabel" aria-hidden="true" data-bs-backdrop="static">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="loginModalLabel">Login</h5>
                </div>
                <div class="modal-body">
                    <div id="loginAlert"></div>
                    <form id="loginForm">
                        <div class="mb-3">
                            <label for="loginEmail" class="form-label">Email address</label>
                            <input type="email" class="form-control" id="loginEmail" required>
                        </div>
                        <div class="mb-3">
                            <label for="loginPassword" class="form-label">Password</label>
                            <input type="password" class="form-control" id="loginPassword" required>
                        </div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">Login</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <!-- Create List Modal -->
    <div class="modal fade" id="createListModal" tabindex="-1" aria-labelledby="createListModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="createListModalLabel">Create Email List</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form id="createListForm">
                        <div class="mb-3">
                            <label for="listName" class="form-label">List Name</label>
                            <input type="text" class="form-control" id="listName" required>
                        </div>
                        <div class="mb-3">
                            <label for="listDescription" class="form-label">Description (optional)</label>
                            <textarea class="form-control" id="listDescription" rows="3"></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" id="saveListBtn">Create List</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Upload Contacts Modal -->
    <div class="modal fade" id="uploadContactsModal" tabindex="-1" aria-labelledby="uploadContactsModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="uploadContactsModalLabel">Upload Contacts</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form id="uploadContactsForm">
                        <div class="mb-3">
                            <label for="contactsFile" class="form-label">CSV File</label>
                            <input type="file" class="form-control" id="contactsFile" accept=".csv,.txt" required>
                            <small class="form-text text-muted">
                                Format: email,first_name,last_name (one per line)
                            </small>
                        </div>
                        <input type="hidden" id="uploadListId" value="">
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" id="uploadContactsBtn">Upload</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Add SMTP Modal -->
    <div class="modal fade" id="addSmtpModal" tabindex="-1" aria-labelledby="addSmtpModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="addSmtpModalLabel">Add SMTP Server</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form id="addSmtpForm">
                        <input type="hidden" id="smtpServerId" value="">
                        <div class="mb-3">
                            <label for="smtpName" class="form-label">Server Name</label>
                            <input type="text" class="form-control" id="smtpName" required>
                        </div>
                        <div class="mb-3">
                            <label for="smtpHost" class="form-label">Host</label>
                            <input type="text" class="form-control" id="smtpHost" required>
                        </div>
                        <div class="mb-3">
                            <label for="smtpPort" class="form-label">Port</label>
                            <input type="number" class="form-control" id="smtpPort" required value="587">
                        </div>
                        <div class="mb-3">
                            <label for="smtpUsername" class="form-label">Username</label>
                            <input type="text" class="form-control" id="smtpUsername" required>
                        </div>
                        <div class="mb-3">
                            <label for="smtpPassword" class="form-label">Password</label>
                            <input type="password" class="form-control" id="smtpPassword" required>
                        </div>
                        <div class="mb-3">
                            <label for="smtpFromEmail" class="form-label">From Email</label>
                            <input type="email" class="form-control" id="smtpFromEmail" required>
                        </div>
                        <div class="mb-3">
                            <label for="smtpFromName" class="form-label">From Name (optional)</label>
                            <input type="text" class="form-control" id="smtpFromName">
                        </div>
                        <div class="mb-3">
                            <label for="smtpMaxEmails" class="form-label">Max Emails Per Day</label>
                            <input type="number" class="form-control" id="smtpMaxEmails" value="500">
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" id="testSmtpBtn">Test Connection</button>
                    <button type="button" class="btn btn-success" id="saveSmtpBtn">Save Server</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Add Proxy Modal -->
    <div class="modal fade" id="addProxyModal" tabindex="-1" aria-labelledby="addProxyModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="addProxyModalLabel">Add Proxy</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form id="addProxyForm">
                        <div class="mb-3">
                            <label for="proxyHost" class="form-label">Host</label>
                            <input type="text" class="form-control" id="proxyHost" required>
                        </div>
                        <div class="mb-3">
                            <label for="proxyPort" class="form-label">Port</label>
                            <input type="number" class="form-control" id="proxyPort" required value="1080">
                        </div>
                        <div class="mb-3">
                            <label for="proxyType" class="form-label">Type</label>
                            <select class="form-select" id="proxyType">
                                <option value="http">HTTP</option>
                                <option value="socks4">SOCKS4</option>
                                <option value="socks5">SOCKS5</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="proxyUsername" class="form-label">Username (optional)</label>
                            <input type="text" class="form-control" id="proxyUsername">
                        </div>
                        <div class="mb-3">
                            <label for="proxyPassword" class="form-label">Password (optional)</label>
                            <input type="password" class="form-control" id="proxyPassword">
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" id="testProxyBtn">Test Connection</button>
                    <button type="button" class="btn btn-success" id="saveProxyBtn">Save Proxy</button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="js/utils.js"></script>
    <script src="js/api_sender.js"></script>
    <script src="js/auth.js"></script>
    <script src="js/dashboard.js"></script>
    <script src="js/lists_sender.js"></script>
    <script src="js/smtp_complete.js"></script>
    <script src="js/proxies_complete.js"></script>
    <script src="js/app_complete.js"></script>
    <script src="js/direct_fixes.js"></script>
</body>
</html>
EOL

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
echo "FIXED APPLICATION IS RUNNING"
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