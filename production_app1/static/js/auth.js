// Authentication functions

// Initialize authentication
function initAuth() {
    // For demo purposes, auto-login
    document.getElementById('userInfo').textContent = 'Demo User';
}

// Login function
async function login(email, password) {
    try {
        // For demo purposes, just return success
        return {
            name: 'Demo User',
            email: email
        };
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
}

// Logout function
function logout() {
    // For demo purposes, just reload the page
    window.location.reload();
}

// Add event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            
            try {
                const user = await login(email, password);
                document.getElementById('userInfo').textContent = user.name;
                
                // Hide login modal
                const loginModal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
                loginModal.hide();
                
                // Show success message
                showAlert('Login successful', 'success');
                
                // Load dashboard
                loadPage('dashboard');
            } catch (error) {
                // Show error message
                document.getElementById('loginAlert').innerHTML = `
                    <div class="alert alert-danger">
                        ${error.message}
                    </div>
                `;
            }
        });
    }
    
    // Logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
});