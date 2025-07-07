// API client for Email Marketing Platform
class API {
    constructor() {
        this.baseUrl = 'http://localhost:5001/api';
    }

    // Helper method for making API requests
    async request(endpoint, method = 'GET', data = null) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json'
        };

        const options = {
            method,
            headers
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            const responseData = await response.json();

            if (!response.ok) {
                throw new Error(responseData.message || `API error: ${response.status}`);
            }

            if (!responseData.success) {
                throw new Error(responseData.message || 'API request failed');
            }

            return responseData;
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    // Lists methods
    async getLists() {
        const response = await this.request('/lists');
        return response.data;
    }

    async createList(name, description = '') {
        const response = await this.request('/lists', 'POST', { name, description });
        return response.data;
    }

    async getList(listId) {
        const response = await this.request(`/lists/${listId}`);
        return response.data;
    }

    async deleteList(listId) {
        const response = await this.request(`/lists/${listId}`, 'DELETE');
        return response;
    }

    async getContacts(listId) {
        const response = await this.request(`/lists/${listId}/contacts`);
        return response.data;
    }

    async addContacts(listId, contacts) {
        const response = await this.request(`/lists/${listId}/contacts`, 'POST', { contacts });
        return response.added_count;
    }

    // Enrichment methods
    async enrichContacts(contacts) {
        const response = await this.request('/enrich', 'POST', { contacts });
        return response.data;
    }

    // SMTP methods
    async getSmtpServers() {
        const response = await this.request('/smtp');
        return response.data;
    }

    async testSmtpServer(host, port, username, password, serverId) {
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
    }

    async addSmtpServer(serverData) {
        const response = await this.request('/smtp', 'POST', serverData);
        return response.data;
    }
    
    async deleteSmtpServer(serverId) {
        const response = await this.request(`/smtp/${serverId}`, 'DELETE');
        return response;
    }

    // Proxies methods
    async getProxies() {
        const response = await this.request('/proxies');
        return response.data;
    }

    async testProxy(host, port, username = '', password = '', proxyType = 'http', proxyId = null) {
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
    }

    async addProxy(proxyData) {
        const response = await this.request('/proxies', 'POST', proxyData);
        return response.data;
    }
    
    async deleteProxy(proxyId) {
        const response = await this.request(`/proxies/${proxyId}`, 'DELETE');
        return response;
    }
}

// Create a singleton instance
window.api = new API();