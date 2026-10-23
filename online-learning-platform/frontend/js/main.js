/**
 * LearnHub - Core Application & Global Utilities
 */

// Dynamically determine API Base URL
// If accessed via localhost:5000 (direct Flask serve), base is ""
// If accessed via Live Server or file:, defaults to http://localhost:5000
const API_BASE = (window.location.port === "5000" || window.location.origin.includes(":5000"))
  ? "" 
  : "http://localhost:5000";

let currentUser = null;

/**
 * Universal JSON Fetch Wrapper with Session Credentials
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const defaultHeaders = {
    "Content-Type": "application/json",
    "Accept": "application/json"
  };

  const config = {
    ...options,
    credentials: "include", // Essential for cross-origin or local cookie sessions
    headers: {
      ...defaultHeaders,
      ...(options.headers || {})
    }
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json().catch(() => ({
      success: false,
      message: `Failed to parse JSON response (HTTP ${response.status})`
    }));

    if (!response.ok && data.success === undefined) {
      data.success = false;
    }

    return { ok: response.ok, status: response.status, data };
  } catch (error) {
    console.error("Network or API Error:", error);
    return {
      ok: false,
      status: 0,
      data: {
        success: false,
        message: "Unable to reach server. Please ensure the backend is running at http://localhost:5000"
      }
    };
  }
}

/**
 * Modern Toast Notifications
 */
function showToast(title, message, type = "info") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;

  const iconMap = {
    success: "fa-circle-check",
    error: "fa-circle-exclamation",
    warning: "fa-triangle-exclamation",
    info: "fa-circle-info"
  };

  toast.innerHTML = `
    <i class="fa-solid ${iconMap[type] || 'fa-circle-info'} toast-icon"></i>
    <div class="toast-body">
      <div class="toast-title">${title}</div>
      <div class="toast-message">${message}</div>
    </div>
    <button class="toast-close" onclick="this.parentElement.remove()">
      <i class="fa-solid fa-xmark"></i>
    </button>
  `;

  container.appendChild(toast);

  // Auto remove after 4.5 seconds
  setTimeout(() => {
    if (toast.parentElement) {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(50px)";
      setTimeout(() => toast.remove(), 300);
    }
  }, 4500);
}

/**
 * Initialize dynamic navbar based on user authentication state
 */
async function initNavbar() {
  const navAuthContainer = document.getElementById("nav-auth-container");
  if (!navAuthContainer) return;

  const res = await apiRequest("/api/auth/me");
  
  if (res.ok && res.data.authenticated && res.data.user) {
    currentUser = res.data.user;
    window.currentUser = currentUser;

    const isAdmin = currentUser.role === "admin";
    const avatar = currentUser.avatar || `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(currentUser.name)}`;

    navAuthContainer.innerHTML = `
      <div style="display: flex; align-items: center; gap: 0.75rem;">
        ${isAdmin ? `
          <a href="admin.html" class="btn btn-sm btn-outline" style="border-color: var(--secondary); color: var(--secondary);">
            <i class="fa-solid fa-shield-halved"></i> Admin Console
          </a>
        ` : `
          <a href="dashboard.html" class="btn btn-sm btn-outline-primary">
            <i class="fa-solid fa-book-open"></i> My Learning
          </a>
        `}
        
        <div class="user-menu-btn" onclick="toggleUserDropdown(event)" id="user-profile-trigger">
          <img src="${avatar}" alt="${currentUser.name}" class="user-avatar" />
          <span class="user-name">${currentUser.name.split(' ')[0]}</span>
          <i class="fa-solid fa-chevron-down" style="font-size: 0.75rem; color: var(--text-muted);"></i>
        </div>

        <button onclick="handleLogout()" class="btn btn-sm btn-outline" title="Log Out">
          <i class="fa-solid fa-arrow-right-from-bracket"></i>
        </button>
      </div>
    `;
  } else {
    currentUser = null;
    window.currentUser = null;
    navAuthContainer.innerHTML = `
      <a href="login.html" class="btn btn-sm btn-outline">Log In</a>
      <a href="register.html" class="btn btn-sm btn-primary">Get Started</a>
    `;
  }

  // Mobile menu toggle listener
  const toggleBtn = document.querySelector(".nav-toggle");
  const navLinks = document.querySelector(".nav-links");
  if (toggleBtn && navLinks) {
    toggleBtn.addEventListener("click", () => {
      navLinks.classList.toggle("open");
    });
  }
}

/**
 * Perform secure logout
 */
async function handleLogout() {
  const res = await apiRequest("/api/auth/logout", { method: "POST" });
  if (res.ok) {
    showToast("Signed Out", "You have been logged out safely.", "success");
    setTimeout(() => {
      window.location.href = "login.html";
    }, 500);
  } else {
    showToast("Error", "Logout failed. Please try again.", "error");
  }
}

/**
 * Helpers for course rendering
 */
function renderRatingStars(rating) {
  const fullStars = Math.floor(rating);
  const hasHalf = rating - fullStars >= 0.5;
  let html = '';
  for (let i = 0; i < fullStars; i++) {
    html += '<i class="fa-solid fa-star"></i>';
  }
  if (hasHalf) {
    html += '<i class="fa-solid fa-star-half-stroke"></i>';
  }
  const remaining = 5 - Math.ceil(rating);
  for (let i = 0; i < remaining; i++) {
    html += '<i class="fa-regular fa-star"></i>';
  }
  return `<span class="rating-stars">${html}</span> <span style="font-weight: 700;">${rating.toFixed(1)}</span>`;
}

function formatPrice(price) {
  if (price === 0 || price === "0" || !price) {
    return `<span style="color: var(--success); font-weight: 800;">Free</span>`;
  }
  return `$${parseFloat(price).toFixed(2)}`;
}

// Global initialization on DOMContentLoaded
document.addEventListener("DOMContentLoaded", () => {
  initNavbar();
});
