// SMTP functionality - Complete version

// Global variables
let smtpServers = [];

// Load SMTP page
async function loadSmtpPage() {
    // Update page title
    document.getElementById('pageTitle').textContent = 'SMTP Servers';
    
    // Add action buttons
    document.getElementById('pageActions').innerHTML = `
        <button class="btn btn-primary" id="addSmtpBtn">
            <i class="fas fa-plus me-1"></i> Add SMTP Server
        </button>
    `;
    
    // Add event listener for add SMTP button
    document.getElementById('addSmtpBtn').addEventListener('click', showAddSmtpModal);
    
    // Load SMTP servers
    await loadSmtpServers();
}

// Load SMTP servers
async function loadSmtpServers() {
    try {
        // Show loading
        document.getElementById('pageContent').innerHTML = `
            <div class="d-flex justify-content-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        
        // Get SMTP servers
        smtpServers = await api.getSmtpServers();
        
        // Build HTML
        let html = '';
        
        if (smtpServers.length === 0) {
            html = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i> No SMTP servers found. Add your first server to get started.
                </div>
            `;
        } else {
            html = `
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">SMTP Servers</h5>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Host</th>
                                    <th>Username</th>
                                    <th>From Email</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${smtpServers.map(server => `
                                    <tr>
                                        <td>${server.name}</td>
                                        <td>${server.host}:${server.port}</td>
                                        <td>${server.username}</td>
                                        <td>${server.from_email}</td>
                                        <td>
                                            <span class="badge bg-${server.status === 'active' ? 'success' : 'danger'}">
                                                ${server.status}
                                            </span>
                                        </td>
                                        <td>
                                            <button class="btn btn-sm btn-primary test-smtp" data-id="${server.id}">
                                                <i class="fas fa-check-circle"></i>
                                            </button>
                                            <button class="btn btn-sm btn-danger delete-smtp" data-id="${server.id}" data-name="${server.name}">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }
        
        // Set content
        document.getElementById('pageContent').innerHTML = html;
        
        // Add event listeners
        document.querySelectorAll('.test-smtp').forEach(button => {
            button.addEventListener('click', function() {
                const serverId = this.getAttribute('data-id');
                testSmtpServer(serverId);
            });
        });
        
        document.querySelectorAll('.delete-smtp').forEach(button => {
            button.addEventListener('click', function() {
                const serverId = this.getAttribute('data-id');
                const serverName = this.getAttribute('data-name');
                deleteSmtpServer(serverId, serverName);
            });
        });
    } catch (error) {
        console.error('Error loading SMTP servers:', error);
        showAlert('Error loading SMTP servers: ' + error.message, 'danger');
    }
}

// Show add SMTP modal
function showAddSmtpModal() {
    // Reset form
    document.getElementById('addSmtpForm').reset();
    document.getElementById('smtpServerId').value = '';
    
    // Update modal title
    document.getElementById('addSmtpModalLabel').textContent = 'Add SMTP Server';
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('addSmtpModal'));
    modal.show();
    
    // Add event listeners
    document.getElementById('testSmtpBtn').onclick = testSmtpConnection;
    document.getElementById('saveSmtpBtn').onclick = saveSmtpServer;
}

// Test SMTP connection
async function testSmtpConnection() {
    try {
        const host = document.getElementById('smtpHost').value.trim();
        const port = document.getElementById('smtpPort').value.trim();
        const username = document.getElementById('smtpUsername').value.trim();
        const password = document.getElementById('smtpPassword').value.trim();
        
        if (!host || !port || !username || !password) {
            showAlert('Please fill in all required fields', 'danger');
            return;
        }
        
        // Disable button
        const testBtn = document.getElementById('testSmtpBtn');
        testBtn.disabled = true;
        testBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Testing...';
        
        console.log('Testing SMTP connection:', { host, port, username });
        
        // Test connection
        const result = await api.testSmtpServer(host, port, username, password);
        
        // Show success message
        showAlert('SMTP connection successful', 'success');
    } catch (error) {
        console.error('Error testing SMTP connection:', error);
        showAlert('Error testing SMTP connection: ' + error.message, 'danger');
    } finally {
        // Reset button
        const testBtn = document.getElementById('testSmtpBtn');
        testBtn.disabled = false;
        testBtn.innerHTML = 'Test Connection';
    }
}

// Save SMTP server
async function saveSmtpServer() {
    try {
        const serverId = document.getElementById('smtpServerId').value.trim();
        const name = document.getElementById('smtpName').value.trim();
        const host = document.getElementById('smtpHost').value.trim();
        const port = document.getElementById('smtpPort').value.trim();
        const username = document.getElementById('smtpUsername').value.trim();
        const password = document.getElementById('smtpPassword').value.trim();
        const fromEmail = document.getElementById('smtpFromEmail').value.trim();
        const fromName = document.getElementById('smtpFromName').value.trim();
        const maxEmailsPerDay = document.getElementById('smtpMaxEmails').value.trim();
        
        if (!name || !host || !port || !username || !password || !fromEmail) {
            showAlert('Please fill in all required fields', 'danger');
            return;
        }
        
        // Disable button
        const saveBtn = document.getElementById('saveSmtpBtn');
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
        
        // Create server data
        const serverData = {
            name,
            host,
            port: parseInt(port),
            username,
            password,
            from_email: fromEmail,
            from_name: fromName,
            max_emails_per_day: parseInt(maxEmailsPerDay)
        };
        
        console.log('Saving SMTP server:', serverData);
        
        // Save server
        await api.addSmtpServer(serverData);
        
        // Hide modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('addSmtpModal'));
        modal.hide();
        
        // Show success message
        showAlert('SMTP server saved successfully', 'success');
        
        // Reload SMTP servers
        await loadSmtpServers();
    } catch (error) {
        console.error('Error saving SMTP server:', error);
        showAlert('Error saving SMTP server: ' + error.message, 'danger');
    } finally {
        // Reset button
        const saveBtn = document.getElementById('saveSmtpBtn');
        saveBtn.disabled = false;
        saveBtn.innerHTML = 'Save Server';
    }
}

// Test SMTP server
async function testSmtpServer(serverId) {
    try {
        // Find server
        const server = smtpServers.find(s => s.id === parseInt(serverId));
        if (!server) {
            showAlert('Server not found', 'danger');
            return;
        }
        
        // Show testing message
        showAlert('Testing SMTP connection...', 'info');
        
        console.log('Testing SMTP server:', serverId);
        
        // Test connection with server ID
        const result = await api.testSmtpServer(server.host, server.port, server.username, '', serverId);
        
        // Show success message
        showAlert('SMTP connection successful', 'success');
    } catch (error) {
        console.error('Error testing SMTP server:', error);
        showAlert('Error testing SMTP server: ' + error.message, 'danger');
    }
}

// Delete SMTP server
async function deleteSmtpServer(serverId, serverName) {
    try {
        // Confirm deletion
        if (!confirm(`Are you sure you want to delete "${serverName}"? This cannot be undone.`)) {
            return;
        }
        
        // Delete server
        await api.deleteSmtpServer(serverId);
        
        // Show success message
        showAlert('SMTP server deleted successfully', 'success');
        
        // Reload SMTP servers
        await loadSmtpServers();
    } catch (error) {
        console.error('Error deleting SMTP server:', error);
        showAlert('Error deleting SMTP server: ' + error.message, 'danger');
    }
}