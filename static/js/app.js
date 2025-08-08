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
    
    // Initialize touch enhancements
    initializeTouchEnhancements();
    
    // Initialize swipe gestures for sidebar navigation
    initializeSidebarSwipeGestures();
    
    // Initialize touch feedback
    initializeTouchFeedback();
    
    // Initialize sidebar navigation
    initializeSidebarNavigation();
    
    // Load initial section
    loadInitialSection();
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
    if (element) {
        // Button loading state
        const originalText = element.innerHTML;
        element.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Loading...';
        element.disabled = true;
        
        return () => {
            element.innerHTML = originalText;
            element.disabled = false;
        };
    } else {
        // Global loading overlay
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'flex';
        }
    }
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
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

// Enhanced keyboard shortcuts for sidebar navigation
document.addEventListener('keydown', function(e) {
    // Number keys for quick section navigation
    if (e.key >= '1' && e.key <= '4') {
        e.preventDefault();
        const sectionIndex = parseInt(e.key) - 1;
        if (sections[sectionIndex]) {
            loadSection(sections[sectionIndex]);
            setActiveNavItem(document.querySelector(`[data-section="${sections[sectionIndex]}"]`));
        }
    }
    
    // Arrow keys for section navigation
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
        e.preventDefault();
        const currentIndex = sections.indexOf(currentSection);
        
        if (e.key === 'ArrowLeft' && currentIndex > 0) {
            loadSection(sections[currentIndex - 1]);
            setActiveNavItem(document.querySelector(`[data-section="${sections[currentIndex - 1]}"]`));
        } else if (e.key === 'ArrowRight' && currentIndex < sections.length - 1) {
            loadSection(sections[currentIndex + 1]);
            setActiveNavItem(document.querySelector(`[data-section="${sections[currentIndex + 1]}"]`));
        }
    }
    
    // Ctrl/Cmd + H = Dashboard
    if ((e.ctrlKey || e.metaKey) && e.key === 'h') {
        e.preventDefault();
        loadSection('dashboard');
        setActiveNavItem(document.querySelector('[data-section="dashboard"]'));
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

// Enhanced visual feedback for touch interactions
function addRippleEffect(element, event) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    
    // Handle both mouse and touch events
    let x, y;
    if (event.touches && event.touches[0]) {
        x = event.touches[0].clientX - rect.left - size / 2;
        y = event.touches[0].clientY - rect.top - size / 2;
    } else {
        x = event.clientX - rect.left - size / 2;
        y = event.clientY - rect.top - size / 2;
    }
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');
    
    element.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

// Add ripple effect to buttons and touch targets
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('btn') || e.target.classList.contains('touch-indicator')) {
        addRippleEffect(e.target, e);
    }
});

// Add touch event listeners for better mobile experience
document.addEventListener('touchstart', function(e) {
    if (e.target.classList.contains('btn') || e.target.classList.contains('touch-indicator')) {
        addRippleEffect(e.target, e);
        e.target.classList.add('touch-feedback');
    }
});

document.addEventListener('touchend', function(e) {
    setTimeout(() => {
        e.target.classList.remove('touch-feedback');
    }, 100);
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

// Touch-specific enhancements for Raspberry Pi
function initializeTouchEnhancements() {
    // Add touch indicator class to interactive elements
    const interactiveElements = document.querySelectorAll('.btn, .nav-link, .card, .alert .btn-close');
    interactiveElements.forEach(element => {
        element.classList.add('touch-indicator');
    });
    
    // Prevent context menu on long press for better touch experience
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
    });
    
    // Add visual feedback for touch targets
    document.addEventListener('touchstart', function(e) {
        e.target.style.transform = 'scale(0.98)';
    });
    
    document.addEventListener('touchend', function(e) {
        setTimeout(() => {
            e.target.style.transform = '';
        }, 100);
    });
}

// Sidebar navigation system
let currentSection = 'dashboard';
const sections = ['dashboard', 'chores', 'meals', 'notifications'];

function initializeSidebarNavigation() {
    const navLinks = document.querySelectorAll('.sidebar-nav .nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.dataset.section) {
                e.preventDefault();
                const section = this.dataset.section;
                loadSection(section);
                setActiveNavItem(this);
            }
        });
    });
}

function loadSection(sectionName) {
    if (sectionName === currentSection) return;
    
    showLoading();
    currentSection = sectionName;
    
    // Determine the URL based on section
    let url;
    switch(sectionName) {
        case 'dashboard':
            url = '/';
            break;
        case 'chores':
            url = '/chores';
            break;
        case 'meals':
            url = '/meal-plans';
            break;
        case 'notifications':
            url = '/notifications';
            break;
        default:
            url = '/';
    }
    
    // Fetch content via AJAX
    fetch(url, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        // Extract content from the response
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newContent = doc.querySelector('main').innerHTML;
        
        // Update the main content
        const mainContent = document.querySelector('.main-content');
        mainContent.innerHTML = newContent;
        
        // Re-initialize interactive elements
        initializeInteractiveElements();
        
        hideLoading();
        
        // Update browser history
        history.pushState({section: sectionName}, '', url);
    })
    .catch(error => {
        console.error('Error loading section:', error);
        hideLoading();
        showToast('Failed to load section. Please try again.', 'error');
    });
}

function setActiveNavItem(activeLink) {
    // Remove active class from all nav links
    document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Add active class to clicked link
    activeLink.classList.add('active');
}

function loadInitialSection() {
    const currentPath = window.location.pathname;
    let initialSection = 'dashboard';
    
    if (currentPath === '/chores') {
        initialSection = 'chores';
    } else if (currentPath === '/meal-plans') {
        initialSection = 'meals';
    } else if (currentPath === '/notifications') {
        initialSection = 'notifications';
    }
    
    // Set active nav item based on current page
    const activeLink = document.querySelector(`[data-section="${initialSection}"]`);
    if (activeLink) {
        setActiveNavItem(activeLink);
    }
    
    currentSection = initialSection;
}

function initializeInteractiveElements() {
    // Re-initialize any interactive elements in the loaded content
    initializeDateInputs();
    initializeTooltips();
    initializeDeleteConfirmations();
    initializeTouchFeedback();
}

// Enhanced swipe gestures for sidebar navigation
function initializeSidebarSwipeGestures() {
    let startX = 0;
    let startY = 0;
    let endX = 0;
    let endY = 0;
    
    const mainContent = document.querySelector('.main-content');
    
    mainContent.addEventListener('touchstart', function(e) {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
    });
    
    mainContent.addEventListener('touchend', function(e) {
        endX = e.changedTouches[0].clientX;
        endY = e.changedTouches[0].clientY;
        handleSwipe();
    });
    
    function handleSwipe() {
        const deltaX = endX - startX;
        const deltaY = endY - startY;
        const minSwipeDistance = 100;
        
        // Horizontal swipes for section navigation
        if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > minSwipeDistance) {
            const currentIndex = sections.indexOf(currentSection);
            
            if (deltaX > 0 && currentIndex > 0) {
                // Swipe right - previous section
                loadSection(sections[currentIndex - 1]);
                setActiveNavItem(document.querySelector(`[data-section="${sections[currentIndex - 1]}"]`));
            } else if (deltaX < 0 && currentIndex < sections.length - 1) {
                // Swipe left - next section
                loadSection(sections[currentIndex + 1]);
                setActiveNavItem(document.querySelector(`[data-section="${sections[currentIndex + 1]}"]`));
            }
        }
        
        // Vertical swipes for actions
        if (Math.abs(deltaY) > Math.abs(deltaX) && Math.abs(deltaY) > minSwipeDistance) {
            if (deltaY < 0) {
                // Swipe up - scroll to top
                mainContent.scrollTo({ top: 0, behavior: 'smooth' });
            }
        }
    }
}

// Handle browser back/forward buttons
window.addEventListener('popstate', function(e) {
    if (e.state && e.state.section) {
        currentSection = e.state.section;
        const activeLink = document.querySelector(`[data-section="${e.state.section}"]`);
        if (activeLink) {
            setActiveNavItem(activeLink);
        }
    }
});

// Enhanced touch feedback system
function initializeTouchFeedback() {
    // Add haptic-like feedback through visual cues
    const touchTargets = document.querySelectorAll('.btn, .nav-link, .card');
    
    touchTargets.forEach(target => {
        target.addEventListener('touchstart', function() {
            this.style.boxShadow = '0 0 20px rgba(var(--bs-primary-rgb), 0.5)';
            this.style.transform = 'scale(0.95)';
        });
        
        target.addEventListener('touchend', function() {
            setTimeout(() => {
                this.style.boxShadow = '';
                this.style.transform = '';
            }, 150);
        });
    });
}

// Touch-friendly confirmation dialogs
function showTouchConfirmDialog(message, onConfirm) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-body text-center p-4">
                    <i class="fas fa-question-circle fa-3x text-warning mb-3"></i>
                    <h4 class="mb-3">${message}</h4>
                    <div class="d-grid gap-3">
                        <button type="button" class="btn btn-danger btn-lg" id="confirm-yes">
                            <i class="fas fa-check me-2"></i>Yes, Continue
                        </button>
                        <button type="button" class="btn btn-secondary btn-lg" id="confirm-no">
                            <i class="fas fa-times me-2"></i>Cancel
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    modal.querySelector('#confirm-yes').addEventListener('click', function() {
        bsModal.hide();
        onConfirm();
        modal.remove();
    });
    
    modal.querySelector('#confirm-no').addEventListener('click', function() {
        bsModal.hide();
        modal.remove();
    });
}

// Enhanced delete confirmations for touch
function initializeDeleteConfirmations() {
    const deleteForms = document.querySelectorAll('form[action*="delete"]');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const itemType = form.action.includes('chore') ? 'chore' : 
                           form.action.includes('meal') ? 'meal plan' : 'item';
            
            showTouchConfirmDialog(
                `Delete this ${itemType}?`,
                () => form.submit()
            );
        });
    });
}

// Touch-optimized keyboard navigation
document.addEventListener('keydown', function(e) {
    // Enhanced keyboard shortcuts for touch screen with on-screen keyboard
    
    // Escape key to close modals or go back
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) modal.hide();
        } else {
            history.back();
        }
    }
    
    // Tab navigation enhancement
    if (e.key === 'Tab') {
        const focusedElement = document.activeElement;
        if (focusedElement) {
            focusedElement.style.outline = '3px solid var(--bs-primary)';
            setTimeout(() => {
                focusedElement.style.outline = '';
            }, 2000);
        }
    }
});

console.log('Family Hub initialized successfully with touch optimizations!');
