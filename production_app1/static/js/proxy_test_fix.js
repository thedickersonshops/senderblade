// Proxy functionality - Fixed version with test fix

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
        
        console.log('Testing proxy:', proxyId);
        
        // Test connection with proxy ID
        const result = await api.testProxy('', '', '', '', '', proxyId);
        
        // Show success message
        showAlert(`Proxy connection successful. Your IP: ${result.ip}`, 'success');
    } catch (error) {
        console.error('Error testing proxy:', error);
        showAlert('Error testing proxy: ' + error.message, 'danger');
    }
}