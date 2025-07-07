// Utility functions

// Show alert message
function showAlert(message, type = 'info', timeout = 5000) {
    // Create alert element
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show`;
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to alert container
    const alertContainer = document.getElementById('alertContainer');
    alertContainer.appendChild(alertElement);
    
    // Auto-dismiss after timeout
    if (timeout > 0) {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertElement);
            bsAlert.close();
        }, timeout);
    }
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Format number with commas
function formatNumber(number) {
    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Validate email
function isValidEmail(email) {
    const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

// Truncate text
function truncateText(text, maxLength = 50) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Parse CSV
function parseCSV(text) {
    const lines = text.split('\n');
    const result = [];
    
    for (const line of lines) {
        if (line.trim() === '') continue;
        
        const parts = line.split(',');
        const email = parts[0]?.trim();
        
        if (email && isValidEmail(email)) {
            result.push({
                email: email,
                first_name: parts[1]?.trim() || '',
                last_name: parts[2]?.trim() || ''
            });
        }
    }
    
    return result;
}