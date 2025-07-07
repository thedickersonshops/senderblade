// API client - Fixed version with test fixes

// Test SMTP server
api.testSmtpServer = async function(host, port, username, password, serverId) {
    const data = {
        host: host,
        port: port,
        username: username,
        password: password
    };
    
    // Add server_id if provided
    if (serverId) {
        data.server_id = serverId;
    }
    
    const response = await this.request('/smtp/test', 'POST', data);
    return response.data;
};

// Test proxy
api.testProxy = async function(host, port, username = '', password = '', proxyType = 'http', proxyId = null) {
    const data = {
        host: host,
        port: port,
        username: username,
        password: password,
        proxy_type: proxyType
    };
    
    // Add proxy_id if provided
    if (proxyId) {
        data.proxy_id = proxyId;
    }
    
    const response = await this.request('/proxy/test', 'POST', data);
    return response.data;
};