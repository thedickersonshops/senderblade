// Main application script

// Page modules
const pages = {
    dashboard: loadDashboardPage,
    lists: loadListsPage,
    smtp: loadSmtpPage,
    proxies: loadProxiesPage
};

// Load page
function loadPage(page) {
    // Update active link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-page') === page) {
            link.classList.add('active');
        }
    });
    
    // Clear page content
    document.getElementById('pageContent').innerHTML = '';
    document.getElementById('pageActions').innerHTML = '';
    
    // Load page content
    if (pages[page]) {
        pages[page]();
    } else {
        // Default to dashboard
        loadDashboardPage();
    }
}

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize authentication
    initAuth();
    
    // Add event listeners for navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            loadPage(page);
        });
    });
    
    // Load default page
    loadPage('dashboard');
});