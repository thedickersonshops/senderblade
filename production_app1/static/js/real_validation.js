// Real validation for SMTP and proxies

// Test SMTP connection with real validation
async function testSmtpConnectionReal() {
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
        
        // Test connection with real validation
        const response = await fetch('http://localhost:5001/api/smtp/real-test', {
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

// Test proxy connection with real validation
async function testProxyConnectionReal() {
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
        
        // Test connection with real validation
        const response = await fetch('http://localhost:5001/api/proxy/real-test', {
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

// Add event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Replace SMTP test button click handler
    const testSmtpBtn = document.getElementById('testSmtpBtn');
    if (testSmtpBtn) {
        testSmtpBtn.onclick = testSmtpConnectionReal;
    }
    
    // Replace proxy test button click handler
    const testProxyBtn = document.getElementById('testProxyBtn');
    if (testProxyBtn) {
        testProxyBtn.onclick = testProxyConnectionReal;
    }
    
    // Fix for modals
    const fixModals = function() {
        // Fix SMTP test button
        const testSmtpBtn = document.getElementById('testSmtpBtn');
        if (testSmtpBtn) {
            testSmtpBtn.onclick = testSmtpConnectionReal;
        }
        
        // Fix proxy test button
        const testProxyBtn = document.getElementById('testProxyBtn');
        if (testProxyBtn) {
            testProxyBtn.onclick = testProxyConnectionReal;
        }
    };
    
    // Fix navigation to ensure fixes are applied after page changes
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            setTimeout(fixModals, 500);
        });
    });
});