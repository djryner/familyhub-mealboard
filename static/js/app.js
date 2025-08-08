// Family Hub Application JavaScript

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Auto-dismiss alerts after 5 seconds
    initializeAlerts();
    
    // Initialize date inputs with today's date minimum
    initializeDateInputs();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Add confirmation dialogs for delete actions
    initializeDeleteConfirmations();
}

function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-dismissible)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

function initializeDateInputs() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    
    dateInputs.forEach(input => {
        if (!input.value) {
            input.min = today;
        }
    });
}

function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function initializeDeleteConfirmations() {
    const deleteForms = document.querySelectorAll('form[action*="delete"]');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const itemType = form.action.includes('chore') ? 'chore' : 
                           form.action.includes('meal') ? 'meal plan' : 'item';
            if (!confirm(`Are you sure you want to delete this ${itemType}? This action cannot be undone.`)) {
                e.preventDefault();
            }
        });
    });
}

// Utility functions for enhanced UX
function showLoading(element) {
    const originalText = element.innerHTML;
    element.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Loading...';
    element.disabled = true;
    
    return () => {
        element.innerHTML = originalText;
        element.disabled = false;
    };
}

function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toastHTML = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="fas fa-${getIconForType(type)} text-${type} me-2"></i>
                <strong class="me-auto">Family Hub</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    // Show toast
    const toast = new bootstrap.Toast(document.getElementById(toastId));
    toast.show();
    
    // Remove toast element after it's hidden
    document.getElementById(toastId).addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

function getIconForType(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Enhanced form validation
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Add event listeners for form validation
document.addEventListener('submit', function(e) {
    const form = e.target;
    if (form.tagName === 'FORM' && !validateForm(form)) {
        e.preventDefault();
        showToast('Please fill in all required fields.', 'warning');
    }
});

// Clear validation styles on input
document.addEventListener('input', function(e) {
    if (e.target.classList.contains('is-invalid')) {
        e.target.classList.remove('is-invalid');
    }
});

// Enhanced chore toggle functionality
function toggleChore(choreId, button) {
    const stopLoading = showLoading(button);
    
    fetch(`/chore/${choreId}/toggle`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (response.ok) {
            location.reload();
        } else {
            throw new Error('Failed to update chore');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Failed to update chore. Please try again.', 'error');
    })
    .finally(stopLoading);
}

// Auto-refresh notifications every 5 minutes if on notifications page
if (window.location.pathname === '/notifications') {
    setInterval(() => {
        // Check for new notifications without full page reload
        fetch('/notifications', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.text())
        .then(html => {
            // Simple check for new content
            const parser = new DOMParser();
            const newDoc = parser.parseFromString(html, 'text/html');
            const newNotifications = newDoc.querySelectorAll('.alert').length;
            const currentNotifications = document.querySelectorAll('.alert').length;
            
            if (newNotifications > currentNotifications) {
                showToast('New notifications available!', 'info');
            }
        })
        .catch(error => console.error('Error checking for new notifications:', error));
    }, 300000); // 5 minutes
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + H = Home
    if ((e.ctrlKey || e.metaKey) && e.key === 'h') {
        e.preventDefault();
        window.location.href = '/';
    }
    
    // Ctrl/Cmd + A = Admin (if logged in)
    if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
        const adminLink = document.querySelector('a[href*="admin"]');
        if (adminLink) {
            e.preventDefault();
            window.location.href = adminLink.href;
        }
    }
});

// Add visual feedback for better UX
function addRippleEffect(element, event) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');
    
    element.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

// Add ripple effect to buttons
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('btn')) {
        addRippleEffect(e.target, e);
    }
});

// Add CSS for ripple effect
const style = document.createElement('style');
style.textContent = `
    .btn {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .is-invalid {
        border-color: #dc3545 !important;
        box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25) !important;
    }
`;
document.head.appendChild(style);

console.log('Family Hub initialized successfully!');
