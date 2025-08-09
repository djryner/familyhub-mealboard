/**
 * @file Main application logic for the Family Hub dashboard.
 * @description This file contains all the client-side JavaScript for initializing
 * the application, handling user interactions, managing UI components, and
 * enhancing the user experience with touch-friendly features.
 */

// --- Global State ---
let currentSection = "dashboard";
const sections = ["dashboard", "chores", "meals", "notifications"];

// --- Initialization ---

/**
 * Main entry point for the application. Fires when the DOM is fully loaded.
 */
document.addEventListener("DOMContentLoaded", function () {
  initializeApp();
  startLiveClock();
});

/**
 * Initializes all core application components and event listeners.
 */
function initializeApp() {
  // Initialize UI components
  initializeAlerts();
  initializeDateInputs();
  initializeTooltips();
  initializeInteractiveElements();

  // Initialize navigation systems
  initializeSidebarNavigation();
  initializeSidebarSwipeGestures();
  loadInitialSection();

  // Initialize event listeners for dynamic content and actions
  addGlobalEventListeners();

  console.log("Family Hub initialized successfully with touch optimizations!");
}

/** Live clock (dashboard only) **/
function startLiveClock() {
  const el = document.getElementById("liveClock");
  if (!el) return; // only on dashboard
  function fmt() {
    const now = new Date();
    // Format: Sat Aug 9 11:53 AM
    const dow = now.toLocaleString(undefined, { weekday: 'short' });
    const mon = now.toLocaleString(undefined, { month: 'short' });
    const day = now.getDate();
    let hours = now.getHours();
    const mins = now.getMinutes().toString().padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12;
    el.textContent = `${dow} ${mon} ${day} ${hours}:${mins} ${ampm}`;
    el.setAttribute('aria-label', el.textContent);
  }
  fmt();
  // Update at the next minute boundary then every minute
  const msToNextMinute = 60000 - (Date.now() % 60000) + 50;
  setTimeout(() => {
    fmt();
    setInterval(fmt, 60000);
  }, msToNextMinute);
}

/**
 * Sets up global event listeners for the document.
 */
function addGlobalEventListeners() {
  // Enhanced form validation on submit
  document.addEventListener("submit", handleFormSubmission);
  // Clear validation styles on input
  document.addEventListener("input", handleFormInput);
  // Enhanced keyboard shortcuts
  document.addEventListener("keydown", handleKeyDown);
  // Handle browser back/forward buttons
  window.addEventListener("popstate", handlePopState);
  // Add ripple effect to buttons and touch targets
  document.addEventListener("click", handleRippleEffect);
  // Add touch event listeners for better mobile experience
  document.addEventListener("touchstart", handleTouchStart);
  document.addEventListener("touchend", handleTouchEnd);
}

/**
 * Re-initializes components that may be recreated in dynamically loaded content.
 */
function initializeInteractiveElements() {
  initializeDateInputs();
  initializeTooltips();
  initializeDeleteConfirmations();
  initializeTouchFeedback();
  initializeTouchEnhancements();
}

// --- UI Component Initializers ---

/**
 * Automatically dismisses non-persistent alerts after 5 seconds.
 */
function initializeAlerts() {
  const alerts = document.querySelectorAll(".alert:not(.alert-dismissible)");
  alerts.forEach((alert) => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });
}

/**
 * Sets the minimum date for all date inputs to today.
 */
function initializeDateInputs() {
  const dateInputs = document.querySelectorAll('input[type="date"]');
  const today = new Date().toISOString().split("T")[0];

  dateInputs.forEach((input) => {
    if (!input.value) {
      input.min = today;
    }
  });
}

/**
 * Initializes Bootstrap tooltips for all elements with the appropriate data attribute.
 */
function initializeTooltips() {
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]'),
  );
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
}

/**
 * Attaches custom confirmation dialogs to forms that perform delete actions.
 */
function initializeDeleteConfirmations() {
  const deleteForms = document.querySelectorAll('form[action*="delete"]');
  deleteForms.forEach((form) => {
    // Prevent multiple listeners by removing any old ones first
    form.removeEventListener("submit", handleDeleteSubmission);
    form.addEventListener("submit", handleDeleteSubmission);
  });
}

// --- Event Handlers ---

/**
 * @param {Event} e The submit event.
 */
function handleDeleteSubmission(e) {
  e.preventDefault();
  const form = e.target;
  const itemType = form.action.includes("chore")
    ? "chore"
    : form.action.includes("meal")
      ? "meal plan"
      : "item";

  showTouchConfirmDialog(`Delete this ${itemType}?`, () => form.submit());
}

/**
 * @param {Event} e The submit event.
 */
function handleFormSubmission(e) {
  const form = e.target;
  if (form.tagName === "FORM" && !validateForm(form)) {
    e.preventDefault();
    showToast("Please fill in all required fields.", "warning");
  }
}

/**
 * @param {Event} e The input event.
 */
function handleFormInput(e) {
  if (e.target.classList.contains("is-invalid")) {
    e.target.classList.remove("is-invalid");
  }
}

/**
 * @param {Event} e The keydown event.
 */
function handleKeyDown(e) {
  // Number keys for quick section navigation (1-4)
  if (e.key >= "1" && e.key <= "4" && !e.metaKey && !e.ctrlKey) {
    e.preventDefault();
    const sectionIndex = parseInt(e.key) - 1;
    if (sections[sectionIndex]) {
      loadSection(sections[sectionIndex]);
      setActiveNavItem(
        document.querySelector(`[data-section="${sections[sectionIndex]}"]`),
      );
    }
  }

  // Arrow keys for section navigation
  if (
    (e.key === "ArrowLeft" || e.key === "ArrowRight") &&
    !e.metaKey &&
    !e.ctrlKey
  ) {
    e.preventDefault();
    const currentIndex = sections.indexOf(currentSection);
    if (e.key === "ArrowLeft" && currentIndex > 0) {
      loadSection(sections[currentIndex - 1]);
      setActiveNavItem(
        document.querySelector(
          `[data-section="${sections[currentIndex - 1]}"]`,
        ),
      );
    } else if (e.key === "ArrowRight" && currentIndex < sections.length - 1) {
      loadSection(sections[currentIndex + 1]);
      setActiveNavItem(
        document.querySelector(
          `[data-section="${sections[currentIndex + 1]}"]`,
        ),
      );
    }
  }

  // Ctrl/Cmd + H for Dashboard
  if ((e.ctrlKey || e.metaKey) && e.key === "h") {
    e.preventDefault();
    loadSection("dashboard");
    setActiveNavItem(document.querySelector('[data-section="dashboard"]'));
  }

  // Ctrl/Cmd + A for Admin
  if ((e.ctrlKey || e.metaKey) && e.key === "a") {
    const adminLink = document.querySelector('a[href*="admin"]');
    if (adminLink) {
      e.preventDefault();
      window.location.href = adminLink.href;
    }
  }

  // Escape key to close modals or go back
  if (e.key === "Escape") {
    const openModal = document.querySelector(".modal.show");
    if (openModal) {
      const modal = bootstrap.Modal.getInstance(openModal);
      if (modal) modal.hide();
    } else {
      history.back();
    }
  }

  // Visual feedback for Tab navigation
  if (e.key === "Tab") {
    const focusedElement = document.activeElement;
    if (focusedElement) {
      focusedElement.style.outline = "3px solid var(--bs-primary)";
      setTimeout(() => {
        focusedElement.style.outline = "";
      }, 2000);
    }
  }
}

/**
 * @param {PopStateEvent} e The popstate event.
 */
function handlePopState(e) {
  if (e.state && e.state.section) {
    currentSection = e.state.section;
    const activeLink = document.querySelector(
      `[data-section="${e.state.section}"]`,
    );
    if (activeLink) {
      setActiveNavItem(activeLink);
    }
  }
}

/**
 * @param {Event} e The click event.
 */
function handleRippleEffect(e) {
  if (
    e.target.classList.contains("btn") ||
    e.target.classList.contains("touch-indicator")
  ) {
    addRippleEffect(e.target, e);
  }
}

/**
 * @param {TouchEvent} e The touchstart event.
 */
function handleTouchStart(e) {
  if (
    e.target.classList.contains("btn") ||
    e.target.classList.contains("touch-indicator")
  ) {
    addRippleEffect(e.target, e);
    e.target.classList.add("touch-feedback");
  }
}

/**
 * @param {TouchEvent} e The touchend event.
 */
function handleTouchEnd(e) {
  setTimeout(() => {
    if (e.target) {
      e.target.classList.remove("touch-feedback");
    }
  }, 100);
}

// --- Core Functionality ---

/**
 * Displays a loading indicator.
 * @param {HTMLElement} [element] - If provided, shows a loading state on the button. Otherwise, shows a global overlay.
 * @returns {Function} A function to call to hide the loading indicator.
 */
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
    const overlay = document.getElementById("loadingOverlay");
    if (overlay) {
      overlay.style.display = "flex";
    }
    // Return a no-op function if no element is provided
    return () => {};
  }
}

/**
 * Hides the global loading overlay.
 */
function hideLoading() {
  const overlay = document.getElementById("loadingOverlay");
  if (overlay) {
    overlay.style.display = "none";
  }
}

/**
 * Shows a toast notification.
 * @param {string} message - The message to display.
 * @param {'info'|'success'|'warning'|'error'} [type='info'] - The type of toast.
 */
function showToast(message, type = "info") {
  let toastContainer = document.querySelector(".toast-container");
  if (!toastContainer) {
    toastContainer = document.createElement("div");
    toastContainer.className = "toast-container position-fixed top-0 end-0 p-3";
    document.body.appendChild(toastContainer);
  }

  const toastId = "toast-" + Date.now();
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

  toastContainer.insertAdjacentHTML("beforeend", toastHTML);
  const toastEl = document.getElementById(toastId);
  const toast = new bootstrap.Toast(toastEl);
  toast.show();

  toastEl.addEventListener("hidden.bs.toast", function () {
    this.remove();
  });
}

/**
 * Gets a Font Awesome icon name based on the toast type.
 * @param {string} type - The toast type.
 * @returns {string} The icon class name.
 */
function getIconForType(type) {
  const icons = {
    success: "check-circle",
    error: "exclamation-circle",
    warning: "exclamation-triangle",
    info: "info-circle",
  };
  return icons[type] || "info-circle";
}

/**
 * Validates a form's required fields.
 * @param {HTMLFormElement} form - The form to validate.
 * @returns {boolean} True if the form is valid, false otherwise.
 */
function validateForm(form) {
  const requiredFields = form.querySelectorAll("[required]");
  let isValid = true;

  requiredFields.forEach((field) => {
    if (!field.value.trim()) {
      field.classList.add("is-invalid");
      isValid = false;
    } else {
      field.classList.remove("is-invalid");
    }
  });

  return isValid;
}

/**
 * Toggles a chore's completion status.
 * @param {string} choreId - The ID of the chore to toggle.
 * @param {HTMLButtonElement} button - The button that was clicked.
 */
function toggleChore(choreId, button) {
  const stopLoading = showLoading(button);

  fetch(`/chore/${choreId}/toggle`, {
    method: "POST", // Use POST for state-changing actions
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
  })
    .then((response) => {
      if (response.ok) {
        location.reload(); // Simple reload on success
      } else {
        throw new Error("Failed to update chore");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showToast("Failed to update chore. Please try again.", "error");
    })
    .finally(stopLoading);
}

// --- Page/Section Navigation ---

/**
 * Loads a new section into the main content area using AJAX.
 * @param {string} sectionName - The name of the section to load.
 */
function loadSection(sectionName) {
  if (sectionName === currentSection) return;

  showLoading();
  currentSection = sectionName;

  const urls = {
    dashboard: "/",
    chores: "/chores",
    meals: "/meal-plans",
    notifications: "/notifications",
  };
  const url = urls[sectionName] || "/";

  fetch(url, {
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
  })
    .then((response) => response.text())
    .then((html) => {
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, "text/html");
      const newContent = doc.querySelector("main").innerHTML;
      const mainContent = document.querySelector(".main-content");

      mainContent.innerHTML = newContent;
      initializeInteractiveElements();
      hideLoading();
      history.pushState({ section: sectionName }, "", url);
    })
    .catch((error) => {
      console.error("Error loading section:", error);
      hideLoading();
      showToast("Failed to load section. Please try again.", "error");
    });
}

/**
 * Sets the 'active' class on the current sidebar navigation item.
 * @param {HTMLElement} activeLink - The nav link to mark as active.
 */
function setActiveNavItem(activeLink) {
  document
    .querySelectorAll(".sidebar-nav .nav-link")
    .forEach((link) => link.classList.remove("active"));
  activeLink.classList.add("active");
}

/**
 * Determines the initial section to load based on the URL path.
 */
function loadInitialSection() {
  const pathMap = {
    "/chores": "chores",
    "/meal-plans": "meals",
    "/notifications": "notifications",
  };
  const initialSection = pathMap[window.location.pathname] || "dashboard";
  const activeLink = document.querySelector(
    `[data-section="${initialSection}"]`,
  );

  if (activeLink) {
    setActiveNavItem(activeLink);
  }
  currentSection = initialSection;
}

// --- Touch and Visual Enhancements ---

/**
 * Initializes enhancements for touch-based interfaces.
 */
function initializeTouchEnhancements() {
  const interactiveElements = document.querySelectorAll(
    ".btn, .nav-link, .card, .alert .btn-close",
  );
  interactiveElements.forEach((element) => {
    element.classList.add("touch-indicator");
  });

  document.addEventListener("contextmenu", (e) => e.preventDefault());
}

/**
 * Adds a visual ripple effect to an element on click/touch.
 * @param {HTMLElement} element - The element to add the ripple to.
 * @param {MouseEvent|TouchEvent} event - The event that triggered the effect.
 */
function addRippleEffect(element, event) {
  const ripple = document.createElement("span");
  const rect = element.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height);
  const eventX = event.touches ? event.touches[0].clientX : event.clientX;
  const eventY = event.touches ? event.touches[0].clientY : event.clientY;
  const x = eventX - rect.left - size / 2;
  const y = eventY - rect.top - size / 2;

  ripple.style.width = ripple.style.height = `${size}px`;
  ripple.style.left = `${x}px`;
  ripple.style.top = `${y}px`;
  ripple.classList.add("ripple");

  element.appendChild(ripple);
  setTimeout(() => ripple.remove(), 600);
}

/**
 * Initializes swipe gestures for sidebar navigation on the main content area.
 */
function initializeSidebarSwipeGestures() {
  let startX = 0;
  let startY = 0;
  const mainContent = document.querySelector(".main-content");

  mainContent.addEventListener("touchstart", (e) => {
    startX = e.touches[0].clientX;
    startY = e.touches[0].clientY;
  });

  mainContent.addEventListener("touchend", (e) => {
    const endX = e.changedTouches[0].clientX;
    const endY = e.changedTouches[0].clientY;
    handleSwipe(startX, startY, endX, endY);
  });
}

/**
 * Handles the logic for swipe gestures.
 * @param {number} startX - The starting X coordinate.
 * @param {number} startY - The starting Y coordinate.
 * @param {number} endX - The ending X coordinate.
 * @param {number} endY - The ending Y coordinate.
 */
function handleSwipe(startX, startY, endX, endY) {
  const deltaX = endX - startX;
  const deltaY = endY - startY;
  const minSwipeDistance = 100;

  if (
    Math.abs(deltaX) > Math.abs(deltaY) &&
    Math.abs(deltaX) > minSwipeDistance
  ) {
    const currentIndex = sections.indexOf(currentSection);
    if (deltaX > 0 && currentIndex > 0) {
      // Swipe right
      loadSection(sections[currentIndex - 1]);
      setActiveNavItem(
        document.querySelector(
          `[data-section="${sections[currentIndex - 1]}"]`,
        ),
      );
    } else if (deltaX < 0 && currentIndex < sections.length - 1) {
      // Swipe left
      loadSection(sections[currentIndex + 1]);
      setActiveNavItem(
        document.querySelector(
          `[data-section="${sections[currentIndex + 1]}"]`,
        ),
      );
    }
  }
}

/**
 * Initializes visual feedback for touch interactions.
 */
function initializeTouchFeedback() {
  const touchTargets = document.querySelectorAll(".btn, .nav-link, .card");
  touchTargets.forEach((target) => {
    target.addEventListener("touchstart", function () {
      this.style.boxShadow = "0 0 20px rgba(var(--bs-primary-rgb), 0.5)";
      this.style.transform = "scale(0.95)";
    });
    target.addEventListener("touchend", function () {
      setTimeout(() => {
        this.style.boxShadow = "";
        this.style.transform = "";
      }, 150);
    });
  });
}

/**
 * Displays a custom, touch-friendly confirmation dialog.
 * @param {string} message - The confirmation message.
 * @param {Function} onConfirm - The callback to execute if the user confirms.
 */
function showTouchConfirmDialog(message, onConfirm) {
  const modal = document.createElement("div");
  modal.className = "modal fade";
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

  modal.querySelector("#confirm-yes").addEventListener("click", () => {
    bsModal.hide();
    onConfirm();
  });
  modal
    .querySelector("#confirm-no")
    .addEventListener("click", () => bsModal.hide());
  modal.addEventListener("hidden.bs.modal", () => modal.remove());
}

// --- Dynamic CSS ---

/**
 * Injects necessary CSS for dynamic components like the ripple effect.
 * Note: In a larger application, this would be in a separate CSS file.
 */
function injectDynamicCSS() {
  const style = document.createElement("style");
  style.textContent = `
        .btn, .touch-indicator {
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
}

injectDynamicCSS();
