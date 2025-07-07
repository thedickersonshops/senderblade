// Proxies functionality - Fixed version

// Global variables
let proxies = [];

// Load proxies page
async function loadProxiesPage() {
    // Update page title
    document.getElementById('pageTitle').textContent = 'Proxies';
    
    // Add action buttons
    document.getElementById('pageActions').innerHTML = `
        <button class="btn btn-primary" id="addProxyBtn">
            <i class="fas fa-plus me-1"></i> Add Proxy
        </button>
    `;
    
    // Add event listener for add proxy button
    document.getElementById('addProxyBtn').addEventListener('click', showAddProxyModal);
    
    // Load proxies
    await loadProxies();
}

// Load proxies
async function loadProxies() {
    try {
        // Show loading
        document.getElementById('pageContent').innerHTML = `
            <div class="d-flex justify-content-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        
        // Get proxies
        proxies = await api.getProxies();
        
        // Build HTML
        let html = '';
        
        if (proxies.length === 0) {
            html = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i> No proxies found. Add your first proxy to get started.
                </div>
            `;
        } else {
            html = `
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Proxies</h5>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Host</th>
                                    <th>Port</th>
                                    <th>Type</th>
                                    <th>Username</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${proxies.map(proxy => `
                                    <tr>
                                        <td>${proxy.host}</td>
                                        <td>${proxy.port}</td>
                                        <td>${proxy.proxy_type}</td>
                                        <td>${proxy.username || '-'}</td>
                                        <td>
                                            <span class="badge bg-${proxy.status === 'active' ? 'success' : 'danger'}">
                                                ${proxy.status}
                                            </span>
                                        </td>
                                        <td>
                                            <button class="btn btn-sm btn-primary test-proxy" data-id="${proxy.id}">
                                                <i class="fas fa-check-circle"></i>
                                            </button>
                                            <button class="btn btn-sm btn-danger delete-proxy" data-id="${proxy.id}" data-host="${proxy.host}">
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
        document.querySelectorAll('.test-proxy').forEach(button => {
            button.addEventListener('click', function() {
                const proxyId = this.getAttribute('data-id');
                testProxy(proxyId);
            });
        });
        
        document.querySelectorAll('.delete-proxy').forEach(button => {
            button.addEventListener('click', function() {
                const proxyId = this.getAttribute('data-id');
                const proxyHost = this.getAttribute('data-host');
                deleteProxy(proxyId, proxyHost);
            });
        });
    } catch (error) {
        console.error('Error loading proxies:', error);
        showAlert('Error loading proxies: ' + error.message, 'danger');
    }
}

// Show add proxy modal
function showAddProxyModal() {
    // Reset form
    document.getElementById('addProxyForm').reset();
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('addProxyModal'));
    modal.show();
    
    // Add event listeners
    document.getElementById('testProxyBtn').onclick = testProxyConnection;
    document.getElementById('saveProxyBtn').onclick = saveProxy;
}

// Test proxy connection
async function testProxyConnection() {
    try {
        const host = document.getElementById('proxyHost').value.trim();
        const port = document.getElementById('proxyPort').value.trim();
        const username = document.getElementById('proxyUsername').value.trim();
        const password = document.getElementById('proxyPassword').value.trim();
        const proxyType = document.getElementById('proxyType').value;
        
        if (!host || !port) {
            showAlert('Host and port are required', 'danger');
            return;
        }
        
        // Disable button
        const testBtn = document.getElementById('testProxyBtn');
        testBtn.disabled = true;
        testBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Testing...';
        
        console.log('Testing proxy connection:', { host, port, username, proxyType });
        
        // Test connection
        const result = await api.testProxy(host, port, username, password, proxyType);
        
        // Show success message
        showAlert(`Proxy connection successful. Your IP: ${result.ip}`, 'success');
    } catch (error) {
        console.error('Error testing proxy connection:', error);
        showAlert('Error testing proxy connection: ' + error.message, 'danger');
    } finally {
        // Reset button
        const testBtn = document.getElementById('testProxyBtn');
        testBtn.disabled = false;
        testBtn.innerHTML = 'Test Connection';
    }
}

// Save proxy
async function saveProxy() {
    try {
        const host = document.getElementById('proxyHost').value.trim();
        const port = document.getElementById('proxyPort').value.trim();
        const username = document.getElementById('proxyUsername').value.trim();
        const password = document.getElementById('proxyPassword').value.trim();
        const proxyType = document.getElementById('proxyType').value;
        
        if (!host || !port) {
            showAlert('Host and port are required', 'danger');
            return;
        }
        
        // Disable button
        const saveBtn = document.getElementById('saveProxyBtn');
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
        
        // Create proxy data
        const proxyData = {
            host,
            port: parseInt(port),
            username,
            password,
            proxy_type: proxyType
        };
        
        console.log('Saving proxy:', proxyData);
        
        // Save proxy
        await api.addProxy(proxyData);
        
        // Hide modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('addProxyModal'));
        modal.hide();
        
        // Show success message
        showAlert('Proxy saved successfully', 'success');
        
        // Reload proxies
        await loadProxies();
    } catch (error) {
        console.error('Error saving proxy:', error);
        showAlert('Error saving proxy: ' + error.message, 'danger');
    } finally {
        // Reset button
        const saveBtn = document.getElementById('saveProxyBtn');
        saveBtn.disabled = false;
        saveBtn.innerHTML = 'Save Proxy';
    }
}

// Test proxy
async function testProxy(proxyId) {
    try {
        // Find proxy
        const proxy = proxies.find(p => p.id === parseInt(proxyId));
        if (!proxy) {
            showAlert('Proxy not found', 'danger');
            return;
        }
        
        // Show testing message
        showAlert('Testing proxy connection...', 'info');
        
        // Test connection
        const result = await api.testProxy(proxy.host, proxy.port, proxy.username, '', proxy.proxy_type);
        
        // Show success message
        showAlert(`Proxy connection successful. Your IP: ${result.ip}`, 'success');
    } catch (error) {
        console.error('Error testing proxy:', error);
        showAlert('Error testing proxy: ' + error.message, 'danger');
    }
}

// Delete proxy
async function deleteProxy(proxyId, proxyHost) {
    try {
        // Confirm deletion
        if (!confirm(`Are you sure you want to delete proxy "${proxyHost}"? This cannot be undone.`)) {
            return;
        }
        
        // Delete proxy
        await api.deleteProxy(proxyId);
        
        // Show success message
        showAlert('Proxy deleted successfully', 'success');
        
        // Reload proxies
        await loadProxies();
    } catch (error) {
        console.error('Error deleting proxy:', error);
        showAlert('Error deleting proxy: ' + error.message, 'danger');
    }
}