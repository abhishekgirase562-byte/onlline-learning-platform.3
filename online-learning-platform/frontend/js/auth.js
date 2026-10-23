/**
 * LearnHub - Authentication Controller (Login & Registration)
 */

document.addEventListener("DOMContentLoaded", () => {
  initLoginForm();
  initRegisterForm();
});

function initLoginForm() {
  const form = document.getElementById("login-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;
    const submitBtn = document.getElementById("login-submit-btn");

    if (!email || !password) {
      showToast("Validation Error", "Please fill in both email and password.", "warning");
      return;
    }

    // Set button loading state
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="spinner"></span> Signing in...`;

    const res = await apiRequest("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });

    submitBtn.disabled = false;
    submitBtn.innerHTML = originalText;

    if (res.ok && res.data.success) {
      showToast("Welcome!", res.data.message || "Signed in successfully", "success");
      
      // Redirect based on role or intended destination
      const user = res.data.user;
      const urlParams = new URLSearchParams(window.location.search);
      const redirect = urlParams.get("redirect");

      setTimeout(() => {
        if (redirect) {
          window.location.href = redirect;
        } else if (user.role === "admin") {
          window.location.href = "admin.html";
        } else {
          window.location.href = "dashboard.html";
        }
      }, 700);
    } else {
      showToast("Login Failed", res.data.message || "Invalid credentials. Please try again.", "error");
    }
  });
}

function initRegisterForm() {
  const form = document.getElementById("register-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("reg-name").value.trim();
    const email = document.getElementById("reg-email").value.trim();
    const password = document.getElementById("reg-password").value;
    const confirmPassword = document.getElementById("reg-confirm-password").value;
    const roleElem = document.getElementById("reg-role");
    const role = roleElem ? roleElem.value : "student";
    const submitBtn = document.getElementById("register-submit-btn");

    // Client-side validations
    if (name.length < 2) {
      showToast("Validation Error", "Full name must be at least 2 characters.", "warning");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      showToast("Validation Error", "Please provide a valid email address.", "warning");
      return;
    }

    if (password.length < 6) {
      showToast("Validation Error", "Password must be at least 6 characters long.", "warning");
      return;
    }

    if (password !== confirmPassword) {
      showToast("Validation Error", "Passwords do not match.", "warning");
      return;
    }

    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="spinner"></span> Creating Account...`;

    const res = await apiRequest("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ name, email, password, role })
    });

    submitBtn.disabled = false;
    submitBtn.innerHTML = originalText;

    if (res.ok && res.data.success) {
      showToast("Account Created", "Your account was successfully registered!", "success");
      setTimeout(() => {
        if (res.data.user.role === "admin") {
          window.location.href = "admin.html";
        } else {
          window.location.href = "dashboard.html";
        }
      }, 800);
    } else {
      showToast("Registration Error", res.data.message || "Registration failed.", "error");
    }
  });
}

/**
 * Convenient demo credentials filler for rapid evaluation
 */
function fillDemoCredentials(type) {
  const emailInput = document.getElementById("login-email");
  const passInput = document.getElementById("login-password");
  if (!emailInput || !passInput) return;

  if (type === "admin") {
    emailInput.value = "admin@learnhub.com";
    passInput.value = "Admin@12345";
    showToast("Demo Loaded", "Loaded administrator credentials. Click Sign In.", "info");
  } else if (type === "student") {
    emailInput.value = "student@learnhub.com";
    passInput.value = "Student@12345";
    showToast("Demo Loaded", "Loaded student credentials. Click Sign In.", "info");
  }
}
