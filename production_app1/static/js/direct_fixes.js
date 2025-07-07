// Direct fixes for critical functionality

// Fix for upload button
document.addEventListener('DOMContentLoaded', function() {
    // Fix upload contacts button
    const fixUploadButton = function() {
        const uploadBtn = document.getElementById('uploadContactsBtn');
        if (uploadBtn) {
            uploadBtn.onclick = function() {
                console.log('Upload button clicked');
                directUploadContacts();
            };
        }
    };
    
    // Fix for modals
    const fixModals = function() {
        // Fix upload modal
        const uploadModal = document.getElementById('uploadContactsModal');
        if (uploadModal) {
            uploadModal.addEventListener('shown.bs.modal', function() {
                console.log('Upload modal shown');
                fixUploadButton();
            });
        }
        
        // Fix SMTP test button
        const testSmtpBtn = document.getElementById('testSmtpBtn');
        if (testSmtpBtn) {
            testSmtpBtn.onclick = function() {
                console.log('Test SMTP button clicked');
                directTestSmtp();
            };
        }
        
        // Fix proxy test button
        const testProxyBtn = document.getElementById('testProxyBtn');
        if (testProxyBtn) {
            testProxyBtn.onclick = function() {
                console.log('Test proxy button clicked');
                directTestProxy();
            };
        }
    };
    
    // Call fixes
    fixModals();
    
    // Fix navigation to ensure fixes are applied after page changes
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            setTimeout(fixModals, 500);
        });
    });
});

// Direct upload contacts function
async function directUploadContacts() {
    try {
        const listId = document.getElementById('uploadListId').value;
        const fileInput = document.getElementById('contactsFile');
        
        if (!fileInput.files || fileInput.files.length === 0) {
            showAlert('Please select a file', 'danger');
            return;
        }
        
        // Disable button
        const uploadBtn = document.getElementById('uploadContactsBtn');
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Uploading...';
        
        // Read file
        const file = fileInput.files[0];
        const reader = new FileReader();
        
        reader.onload = async function(e) {
            try {
                const content = e.target.result;
                console.log('File content length:', content.length);
                
                // Parse CSV
                const lines = content.split('\n').filter(line => line.trim() !== '');
                const contacts = [];
                
                lines.forEach(line => {
                    const parts = line.split(',');
                    const email = parts[0]?.trim();
                    if (email && email.includes('@')) {
                        contacts.push({
                            email: email,
                            first_name: parts[1]?.trim() || '',
                            last_name: parts[2]?.trim() || ''
                        });
                    }
                });
                
                console.log('Parsed contacts:', contacts.length);
                
                if (contacts.length === 0) {
                    showAlert('No valid contacts found in the file', 'danger');
                    uploadBtn.disabled = false;
                    uploadBtn.innerHTML = 'Upload';
                    return;
                }
                
                // Upload contacts
                const response = await fetch(`http://localhost:5001/api/lists/${listId}/contacts`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ contacts: contacts })
                });
                
                const data = await response.json();
                
                if (!data.success) {
                    throw new Error(data.message || 'Failed to upload contacts');
                }
                
                // Hide modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('uploadContactsModal'));
                modal.hide();
                
                // Show success message
                showAlert(`${data.added_count} contacts added successfully`, 'success');
                
                // Reload list view
                if (typeof viewList === 'function') {
                    viewList(listId);
                } else {
                    window.location.reload();
                }
            } catch (error) {
                console.error('Error processing file:', error);
                showAlert('Error processing file: ' + error.message, 'danger');
                
                // Reset button
                uploadBtn.disabled = false;
                uploadBtn.innerHTML = 'Upload';
            }
        };
        
        reader.readAsText(file);
    } catch (error) {
        console.error('Error uploading contacts:', error);
        showAlert('Error uploading contacts: ' + error.message, 'danger');
        
        // Reset button
        const uploadBtn = document.getElementById('uploadContactsBtn');
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = 'Upload';
    }
}

// Direct test SMTP function
async function directTestSmtp() {
    try {
        const host = document.getElementById('smtpHost').value.trim();
        const port = document.getElementById('smtpPort').value.trim();
        const username = document.getElementById('smtpUsername').value.trim();
        const password = document.getElementById('smtpPassword').value.trim();
        
        if (!host || !port || !username || !password) {
            showAlert('Please fill in all required fields', 'danger');
            return;
        }
        
        // Validate email format for username if it looks like an email
        if (username.includes('@')) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(username)) {
                showAlert('Invalid email format for username', 'danger');
                return;
            }
        }
        
        // Validate password length
        if (password.length < 8) {
            showAlert('Password must be at least 8 characters long', 'danger');
            return;
        }
        
        // Disable button
        const testBtn = document.getElementById('testSmtpBtn');
        testBtn.disabled = true;
        testBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Testing...';
        
        console.log('Testing SMTP connection:', { host, port, username });
        
        // Test connection
        const response = await fetch('http://localhost:5001/api/smtp/test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                host: host, 
                port: parseInt(port), 
                username: username, 
                password: password 
            })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.message || 'SMTP connection failed');
        }
        
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

// Direct test proxy function
async function directTestProxy() {
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
        
        // Validate port
        const portNum = parseInt(port);
        if (isNaN(portNum) || portNum < 1 || portNum > 65535) {
            showAlert('Port must be a number between 1 and 65535', 'danger');
            return;
        }
        
        // Disable button
        const testBtn = document.getElementById('testProxyBtn');
        testBtn.disabled = true;
        testBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Testing...';
        
        console.log('Testing proxy connection:', { host, port, username, proxyType });
        
        // Test connection
        const response = await fetch('http://localhost:5001/api/proxy/test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                host: host, 
                port: parseInt(port), 
                username: username, 
                password: password,
                proxy_type: proxyType
            })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.message || 'Proxy connection failed');
        }
        
        // Show success message
        showAlert(`Proxy connection successful. Your IP: ${data.data.ip}`, 'success');
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