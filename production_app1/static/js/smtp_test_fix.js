// SMTP functionality - Fixed version with test fix

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