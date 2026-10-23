/**
 * LearnHub - Student Dashboard Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  initDashboard();
});

async function initDashboard() {
  const root = document.getElementById("dashboard-root");
  if (!root) return;

  // Verify authentication
  const authRes = await apiRequest("/api/auth/me");
  if (!authRes.ok || !authRes.data.authenticated || !authRes.data.user) {
    showToast("Authentication Required", "Please log in to view your student dashboard.", "warning");
    setTimeout(() => {
      window.location.href = "login.html?redirect=dashboard.html";
    }, 800);
    return;
  }

  const user = authRes.data.user;

  // Load student enrollment and progress data
  const res = await apiRequest("/api/enrollments/my-courses");
  if (!res.ok || !res.data.success) {
    root.innerHTML = `
      <div class="empty-state container">
        <i class="fa-solid fa-triangle-exclamation empty-state-icon" style="color: var(--danger);"></i>
        <h3>Failed to load your learning dashboard</h3>
        <p style="color: var(--text-muted);">${res.data.message || 'Please verify the backend server is running.'}</p>
        <button class="btn btn-primary" onclick="initDashboard()" style="margin-top: 1rem;">Retry</button>
      </div>
    `;
    return;
  }

  const { stats, enrolled_courses } = res.data.data;

  root.innerHTML = `
    <!-- Dashboard Header -->
    <section class="dashboard-header">
      <div class="container user-welcome-card">
        <div class="user-welcome-profile">
          <img src="${user.avatar || 'https://api.dicebear.com/7.x/initials/svg?seed=' + encodeURIComponent(user.name)}" alt="${user.name}" class="profile-avatar-lg" />
          <div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <h1 style="font-size: 1.8rem;">Welcome back, ${user.name}!</h1>
              <span class="badge badge-primary">${user.role}</span>
            </div>
            <p style="color: var(--text-muted); font-size: 0.95rem; margin-top: 0.2rem;">
              ${user.email} • ${user.bio || 'Continuous learner tracking mastery at LearnHub'}
            </p>
          </div>
        </div>

        <div style="display: flex; gap: 0.75rem;">
          <a href="courses.html" class="btn btn-outline-primary">
            <i class="fa-solid fa-magnifying-glass"></i> Browse Catalog
          </a>
          <button onclick="openProfileModal('${user.name}', '${user.bio || ''}')" class="btn btn-outline">
            <i class="fa-solid fa-user-pen"></i> Edit Profile
          </button>
        </div>
      </div>
    </section>

    <!-- Main Dashboard Area -->
    <section class="section" style="padding-top: 2rem;">
      <div class="container">
        <!-- Stats Row -->
        <div class="stats-grid">
          <div class="dashboard-stat-card">
            <div class="stat-icon-wrap icon-blue">
              <i class="fa-solid fa-graduation-cap"></i>
            </div>
            <div>
              <div style="font-family: var(--font-heading); font-size: 1.8rem; font-weight: 800;">${stats.total_enrolled}</div>
              <div style="font-size: 0.85rem; color: var(--text-muted);">Enrolled Courses</div>
            </div>
          </div>

          <div class="dashboard-stat-card">
            <div class="stat-icon-wrap icon-purple">
              <i class="fa-solid fa-clock-rotate-left"></i>
            </div>
            <div>
              <div style="font-family: var(--font-heading); font-size: 1.8rem; font-weight: 800;">${stats.in_progress}</div>
              <div style="font-size: 0.85rem; color: var(--text-muted);">In Progress</div>
            </div>
          </div>

          <div class="dashboard-stat-card">
            <div class="stat-icon-wrap icon-green">
              <i class="fa-solid fa-circle-check"></i>
            </div>
            <div>
              <div style="font-family: var(--font-heading); font-size: 1.8rem; font-weight: 800;">${stats.completed_lessons}</div>
              <div style="font-size: 0.85rem; color: var(--text-muted);">Lessons Completed</div>
            </div>
          </div>

          <div class="dashboard-stat-card">
            <div class="stat-icon-wrap icon-cyan">
              <i class="fa-solid fa-chart-line"></i>
            </div>
            <div>
              <div style="font-family: var(--font-heading); font-size: 1.8rem; font-weight: 800;">${stats.average_progress}%</div>
              <div style="font-size: 0.85rem; color: var(--text-muted);">Avg. Completion Rate</div>
            </div>
          </div>
        </div>

        <!-- Section Heading -->
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem;">
          <h2 style="font-size: 1.5rem;">My Enrolled Courses</h2>
          <span style="font-size: 0.9rem; color: var(--text-muted);">${enrolled_courses.length} Active Enrollments</span>
        </div>

        <!-- Enrolled Courses List -->
        <div id="enrolled-courses-container">
          ${enrolled_courses.length === 0 ? `
            <div class="empty-state" style="background: #fff; border-radius: var(--radius-lg); border: 1px solid var(--border);">
              <i class="fa-solid fa-book-open-reader empty-state-icon" style="color: var(--primary);"></i>
              <h3>You haven't enrolled in any courses yet</h3>
              <p style="color: var(--text-muted); max-width: 440px; margin: 0.5rem auto 1.5rem;">
                Explore our catalog of expert-led courses and start your learning journey today.
              </p>
              <a href="courses.html" class="btn btn-primary">
                <i class="fa-solid fa-compass"></i> Explore Courses
              </a>
            </div>
          ` : enrolled_courses.map(course => `
            <div class="enrolled-course-card">
              <img src="${course.thumbnail || 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80'}" alt="${course.title}" class="enrolled-thumb" />

              <div class="enrolled-info">
                <div style="display: flex; gap: 0.5rem; margin-bottom: 0.4rem;">
                  <span class="badge badge-primary">${course.category}</span>
                  <span class="badge" style="background: var(--bg-alt);">${course.difficulty}</span>
                </div>

                <h3><a href="course-details.html?id=${course.course_id}">${course.title}</a></h3>
                <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.8rem;">
                  Instructor: <strong>${course.instructor ? course.instructor.name : 'LearnHub Instructor'}</strong>
                </p>

                <!-- Progress Bar -->
                <div>
                  <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.3rem;">
                    <span>${course.completed_lessons_count} of ${course.total_lessons} lessons completed</span>
                    <span style="color: var(--primary);">${course.progress_percentage}%</span>
                  </div>
                  <div class="progress-bar-wrap">
                    <div class="progress-bar-fill" style="width: ${course.progress_percentage}%;"></div>
                  </div>
                </div>
              </div>

              <div>
                <a href="lesson.html?course_id=${course.course_id}&lesson_id=${course.next_lesson_id || ''}" class="btn btn-primary">
                  <i class="fa-solid fa-play"></i> Continue Learning
                </a>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    </section>

    <!-- Profile Edit Modal -->
    <div id="profile-modal" class="modal-backdrop">
      <div class="modal-dialog">
        <div class="modal-header">
          <h3 style="font-size: 1.25rem;">Edit Student Profile</h3>
          <button class="toast-close" onclick="closeProfileModal()"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">Full Name</label>
            <input type="text" id="profile-name-input" class="form-control no-icon" />
          </div>
          <div class="form-group">
            <label class="form-label">Short Bio / Learning Goals</label>
            <textarea id="profile-bio-input" class="form-control no-icon" rows="3" placeholder="Tell us about yourself..."></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" onclick="closeProfileModal()">Cancel</button>
          <button class="btn btn-primary" onclick="saveProfileChanges()" id="save-profile-btn">Save Changes</button>
        </div>
      </div>
    </div>
  `;
}

function openProfileModal(name, bio) {
  const modal = document.getElementById("profile-modal");
  const nameInput = document.getElementById("profile-name-input");
  const bioInput = document.getElementById("profile-bio-input");
  if (modal && nameInput && bioInput) {
    nameInput.value = name;
    bioInput.value = bio;
    modal.classList.add("open");
  }
}

function closeProfileModal() {
  const modal = document.getElementById("profile-modal");
  if (modal) modal.classList.remove("open");
}

async function saveProfileChanges() {
  const name = document.getElementById("profile-name-input").value.trim();
  const bio = document.getElementById("profile-bio-input").value.trim();
  const saveBtn = document.getElementById("save-profile-btn");

  if (!name) {
    showToast("Validation Error", "Name cannot be empty.", "warning");
    return;
  }

  saveBtn.disabled = true;
  saveBtn.innerHTML = `<span class="spinner"></span> Saving...`;

  const res = await apiRequest("/api/auth/profile", {
    method: "PUT",
    body: JSON.stringify({ name, bio })
  });

  saveBtn.disabled = false;
  saveBtn.textContent = "Save Changes";

  if (res.ok && res.data.success) {
    showToast("Profile Updated", "Your profile details have been saved.", "success");
    closeProfileModal();
    initDashboard(); // Re-render with new name
  } else {
    showToast("Update Error", res.data.message || "Failed to update profile.", "error");
  }
}
