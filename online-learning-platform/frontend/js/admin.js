/**
 * LearnHub - Admin Dashboard Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  initAdmin();
});

let adminStats = null;
let adminCourses = [];
let adminStudents = [];
let adminEnrollments = [];
let editingCourseId = null;

async function initAdmin() {
  const root = document.getElementById("admin-root");
  if (!root) return;

  // Verify admin access
  const authRes = await apiRequest("/api/auth/me");
  if (!authRes.ok || !authRes.data.authenticated || authRes.data.user?.role !== "admin") {
    showToast("Access Denied", "Administrator access required.", "error");
    setTimeout(() => { window.location.href = "login.html?redirect=admin.html"; }, 900);
    return;
  }

  const user = authRes.data.user;

  root.innerHTML = `
    <section class="dashboard-header">
      <div class="container user-welcome-card">
        <div class="user-welcome-profile">
          <img src="${user.avatar || 'https://api.dicebear.com/7.x/initials/svg?seed=' + encodeURIComponent(user.name)}" alt="${user.name}" class="profile-avatar-lg"/>
          <div>
            <div style="display:flex;align-items:center;gap:0.6rem;">
              <h1 style="font-size:1.8rem;">Admin Console</h1>
              <span class="badge badge-danger"><i class="fa-solid fa-shield-halved"></i> ADMIN</span>
            </div>
            <p style="color:var(--text-muted);margin-top:0.2rem;">Signed in as ${user.name} &bull; ${user.email}</p>
          </div>
        </div>
        <button onclick="handleLogout()" class="btn btn-outline btn-sm">
          <i class="fa-solid fa-arrow-right-from-bracket"></i> Logout
        </button>
      </div>
    </section>

    <section class="section" style="padding-top:2rem;">
      <div class="container">
        <!-- Stats -->
        <div class="stats-grid" id="admin-stats-grid">
          <div class="dashboard-stat-card"><div class="spinner spinner-primary"></div></div>
        </div>

        <!-- Tabs -->
        <div class="tabs-nav">
          <button class="tab-btn active" onclick="switchTab('courses', this)"><i class="fa-solid fa-book"></i> Courses</button>
          <button class="tab-btn" onclick="switchTab('students', this)"><i class="fa-solid fa-users"></i> Students</button>
          <button class="tab-btn" onclick="switchTab('enrollments', this)"><i class="fa-solid fa-list-check"></i> Enrollments</button>
        </div>

        <!-- Tab Panes -->
        <div id="tab-courses" class="tab-pane active">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1.25rem;">
            <h2 style="font-size:1.25rem;">Manage Courses</h2>
            <button class="btn btn-primary" onclick="openCourseModal(null)">
              <i class="fa-solid fa-plus"></i> Add New Course
            </button>
          </div>
          <div id="admin-courses-table">
            <div style="text-align:center;padding:3rem;"><div class="spinner spinner-primary"></div></div>
          </div>
        </div>

        <div id="tab-students" class="tab-pane">
          <h2 style="font-size:1.25rem;margin-bottom:1.25rem;">Registered Students</h2>
          <div id="admin-students-table">
            <div style="text-align:center;padding:3rem;"><div class="spinner spinner-primary"></div></div>
          </div>
        </div>

        <div id="tab-enrollments" class="tab-pane">
          <h2 style="font-size:1.25rem;margin-bottom:1.25rem;">All Enrollments</h2>
          <div id="admin-enrollments-table">
            <div style="text-align:center;padding:3rem;"><div class="spinner spinner-primary"></div></div>
          </div>
        </div>
      </div>
    </section>

    <!-- Course CRUD Modal -->
    <div id="course-modal" class="modal-backdrop">
      <div class="modal-dialog" style="max-width:750px;">
        <div class="modal-header">
          <h3 id="course-modal-title" style="font-size:1.25rem;">Add New Course</h3>
          <button class="toast-close" onclick="closeCourseModal()"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <div class="modal-body">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
            <div class="form-group">
              <label class="form-label">Course Title *</label>
              <input type="text" id="course-title" class="form-control no-icon" placeholder="e.g. React Masterclass" />
            </div>
            <div class="form-group">
              <label class="form-label">Category</label>
              <select id="course-category" class="form-control no-icon select-control">
                <option value="Web Development">Web Development</option>
                <option value="Data Science">Data Science</option>
                <option value="UI/UX Design">UI/UX Design</option>
                <option value="Cloud & DevOps">Cloud & DevOps</option>
                <option value="Cybersecurity">Cybersecurity</option>
                <option value="Mobile Development">Mobile Development</option>
                <option value="Business">Business</option>
                <option value="General">General</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Difficulty</label>
              <select id="course-difficulty" class="form-control no-icon select-control">
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
                <option value="All Levels">All Levels</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Price ($)</label>
              <input type="number" id="course-price" class="form-control no-icon" min="0" step="0.01" value="0" />
            </div>
            <div class="form-group">
              <label class="form-label">Duration</label>
              <input type="text" id="course-duration" class="form-control no-icon" placeholder="e.g. 8h 30m" />
            </div>
            <div class="form-group">
              <label class="form-label">Rating (1-5)</label>
              <input type="number" id="course-rating" class="form-control no-icon" min="1" max="5" step="0.1" value="4.8" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Thumbnail URL</label>
            <input type="text" id="course-thumbnail" class="form-control no-icon" placeholder="https://images.unsplash.com/..." />
          </div>
          <div class="form-group">
            <label class="form-label">Short Description</label>
            <input type="text" id="course-short-desc" class="form-control no-icon" placeholder="Brief marketing description..." />
          </div>
          <div class="form-group">
            <label class="form-label">Full Description</label>
            <textarea id="course-description" class="form-control no-icon" rows="3" placeholder="Detailed course description..."></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">Instructor Name</label>
            <input type="text" id="instructor-name" class="form-control no-icon" />
          </div>
          <div class="form-group">
            <label class="form-label">Instructor Title</label>
            <input type="text" id="instructor-title" class="form-control no-icon" placeholder="e.g. Senior Software Engineer" />
          </div>
          <div class="form-group">
            <label style="display:flex;align-items:center;gap:0.5rem;cursor:pointer;">
              <input type="checkbox" id="course-featured" />
              <span class="form-label" style="margin-bottom:0;">Featured Course (shown on homepage)</span>
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" onclick="closeCourseModal()">Cancel</button>
          <button class="btn btn-primary" id="save-course-btn" onclick="saveCourse()">
            <i class="fa-solid fa-floppy-disk"></i> Save Course
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div id="confirm-modal" class="modal-backdrop">
      <div class="modal-dialog" style="max-width:440px;">
        <div class="modal-header">
          <h3 style="font-size:1.1rem;">Confirm Delete</h3>
          <button class="toast-close" onclick="closeConfirmModal()"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <div class="modal-body">
          <p id="confirm-modal-msg" style="color:var(--text-muted);">Are you sure? This action cannot be undone.</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" onclick="closeConfirmModal()">Cancel</button>
          <button class="btn btn-danger" id="confirm-delete-btn" onclick="">
            <i class="fa-solid fa-trash"></i> Delete Permanently
          </button>
        </div>
      </div>
    </div>
  `;

  await loadAdminData();
}

async function loadAdminData() {
  const [statsRes, coursesRes, studentsRes, enrollmentsRes] = await Promise.all([
    apiRequest("/api/admin/stats"),
    apiRequest("/api/courses"),
    apiRequest("/api/admin/students"),
    apiRequest("/api/admin/enrollments")
  ]);

  if (statsRes.ok) {
    adminStats = statsRes.data.stats;
    renderAdminStats();
  }

  if (coursesRes.ok) {
    adminCourses = coursesRes.data.courses || [];
    renderCoursesTable();
  }

  if (studentsRes.ok) {
    adminStudents = studentsRes.data.students || [];
    renderStudentsTable();
  }

  if (enrollmentsRes.ok) {
    adminEnrollments = enrollmentsRes.data.enrollments || [];
    renderEnrollmentsTable();
  }
}

function renderAdminStats() {
  const grid = document.getElementById("admin-stats-grid");
  if (!grid || !adminStats) return;
  grid.innerHTML = `
    <div class="dashboard-stat-card"><div class="stat-icon-wrap icon-blue"><i class="fa-solid fa-book"></i></div>
      <div><div style="font-family:var(--font-heading);font-size:1.8rem;font-weight:800;">${adminStats.total_courses}</div><div style="font-size:0.85rem;color:var(--text-muted);">Total Courses</div></div>
    </div>
    <div class="dashboard-stat-card"><div class="stat-icon-wrap icon-purple"><i class="fa-solid fa-users"></i></div>
      <div><div style="font-family:var(--font-heading);font-size:1.8rem;font-weight:800;">${adminStats.total_students}</div><div style="font-size:0.85rem;color:var(--text-muted);">Registered Students</div></div>
    </div>
    <div class="dashboard-stat-card"><div class="stat-icon-wrap icon-green"><i class="fa-solid fa-list-check"></i></div>
      <div><div style="font-family:var(--font-heading);font-size:1.8rem;font-weight:800;">${adminStats.total_enrollments}</div><div style="font-size:0.85rem;color:var(--text-muted);">Total Enrollments</div></div>
    </div>
    <div class="dashboard-stat-card"><div class="stat-icon-wrap icon-cyan"><i class="fa-solid fa-play-circle"></i></div>
      <div><div style="font-family:var(--font-heading);font-size:1.8rem;font-weight:800;">${adminStats.total_lessons}</div><div style="font-size:0.85rem;color:var(--text-muted);">Total Lessons</div></div>
    </div>
  `;
}

function renderCoursesTable() {
  const container = document.getElementById("admin-courses-table");
  if (!container) return;
  if (adminCourses.length === 0) {
    container.innerHTML = `<div class="empty-state"><i class="fa-solid fa-book empty-state-icon"></i><h3>No Courses Yet</h3></div>`;
    return;
  }
  container.innerHTML = `
    <div class="table-responsive">
      <table class="table">
        <thead><tr>
          <th>Course</th><th>Category</th><th>Difficulty</th><th>Price</th><th>Lessons</th><th>Students</th><th>Actions</th>
        </tr></thead>
        <tbody>
          ${adminCourses.map(course => `
            <tr>
              <td>
                <div style="display:flex;align-items:center;gap:0.75rem;">
                  <img src="${course.thumbnail}" alt="${course.title}" style="width:50px;height:38px;border-radius:6px;object-fit:cover;" />
                  <div>
                    <div style="font-weight:600;font-size:0.9rem;">${course.title}</div>
                    ${course.featured ? `<span class="badge badge-featured" style="font-size:0.65rem;"><i class="fa-solid fa-bolt"></i> Featured</span>` : ''}
                  </div>
                </div>
              </td>
              <td><span class="badge badge-primary">${course.category}</span></td>
              <td>${course.difficulty}</td>
              <td>${formatPrice(course.price)}</td>
              <td>${course.lessons ? course.lessons.length : 0}</td>
              <td>${course.students_enrolled || 0}</td>
              <td>
                <div style="display:flex;gap:0.5rem;">
                  <button class="btn btn-sm btn-outline-primary" onclick="openCourseModal('${course.id}')">
                    <i class="fa-solid fa-pencil"></i>
                  </button>
                  <button class="btn btn-sm btn-danger" onclick="confirmDeleteCourse('${course.id}', '${course.title.replace(/'/g, "\\'")}')">
                    <i class="fa-solid fa-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function renderStudentsTable() {
  const container = document.getElementById("admin-students-table");
  if (!container) return;
  if (adminStudents.length === 0) {
    container.innerHTML = `<div class="empty-state"><i class="fa-solid fa-users empty-state-icon"></i><h3>No Students Registered Yet</h3></div>`;
    return;
  }
  container.innerHTML = `
    <div class="table-responsive">
      <table class="table">
        <thead><tr><th>Student</th><th>Email</th><th>Role</th><th>Enrollments</th><th>Joined</th></tr></thead>
        <tbody>
          ${adminStudents.map(s => `
            <tr>
              <td>
                <div style="display:flex;align-items:center;gap:0.75rem;">
                  <img src="${s.avatar || 'https://api.dicebear.com/7.x/initials/svg?seed=' + encodeURIComponent(s.name)}" style="width:36px;height:36px;border-radius:50%;object-fit:cover;" />
                  <span style="font-weight:600;">${s.name}</span>
                </div>
              </td>
              <td style="color:var(--text-muted);">${s.email}</td>
              <td><span class="badge ${s.role === 'admin' ? 'badge-danger' : 'badge-primary'}">${s.role}</span></td>
              <td>${s.enrollments_count || 0}</td>
              <td style="color:var(--text-muted);font-size:0.85rem;">${s.created_at ? new Date(s.created_at).toLocaleDateString() : 'N/A'}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function renderEnrollmentsTable() {
  const container = document.getElementById("admin-enrollments-table");
  if (!container) return;
  if (adminEnrollments.length === 0) {
    container.innerHTML = `<div class="empty-state"><i class="fa-solid fa-list-check empty-state-icon"></i><h3>No Enrollments Yet</h3></div>`;
    return;
  }
  container.innerHTML = `
    <div class="table-responsive">
      <table class="table">
        <thead><tr><th>Student</th><th>Course</th><th>Progress</th><th>Status</th><th>Enrolled On</th></tr></thead>
        <tbody>
          ${adminEnrollments.map(enr => `
            <tr>
              <td>
                <div style="font-weight:600;">${enr.student_name}</div>
                <div style="font-size:0.8rem;color:var(--text-muted);">${enr.student_email}</div>
              </td>
              <td style="max-width:200px;font-size:0.9rem;">${enr.course_title}</td>
              <td>
                <div style="min-width:140px;">
                  <div style="display:flex;justify-content:space-between;font-size:0.78rem;font-weight:600;margin-bottom:0.2rem;">
                    <span>${enr.progress_percentage}%</span>
                    ${enr.is_completed ? `<span style="color:var(--success);">Completed</span>` : ''}
                  </div>
                  <div class="progress-bar-wrap" style="height:6px;"><div class="progress-bar-fill" style="width:${enr.progress_percentage}%;"></div></div>
                </div>
              </td>
              <td><span class="badge ${enr.status === 'active' ? 'badge-success' : 'badge-warning'}">${enr.status}</span></td>
              <td style="color:var(--text-muted);font-size:0.85rem;">${enr.enrolled_at ? new Date(enr.enrolled_at).toLocaleDateString() : 'N/A'}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function switchTab(tabName, btn) {
  document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  const pane = document.getElementById(`tab-${tabName}`);
  if (pane) pane.classList.add("active");
  if (btn) btn.classList.add("active");
}

function openCourseModal(courseId) {
  editingCourseId = courseId || null;
  const modal = document.getElementById("course-modal");
  const title = document.getElementById("course-modal-title");
  const saveBtn = document.getElementById("save-course-btn");

  if (courseId) {
    const course = adminCourses.find(c => c.id === courseId);
    if (course) {
      document.getElementById("course-title").value = course.title || "";
      document.getElementById("course-category").value = course.category || "Web Development";
      document.getElementById("course-difficulty").value = course.difficulty || "Beginner";
      document.getElementById("course-price").value = course.price || 0;
      document.getElementById("course-duration").value = course.duration || "";
      document.getElementById("course-rating").value = course.rating || 4.8;
      document.getElementById("course-thumbnail").value = course.thumbnail || "";
      document.getElementById("course-short-desc").value = course.short_description || "";
      document.getElementById("course-description").value = course.description || "";
      document.getElementById("instructor-name").value = course.instructor?.name || "";
      document.getElementById("instructor-title").value = course.instructor?.title || "";
      document.getElementById("course-featured").checked = course.featured || false;
    }
    title.textContent = "Edit Course";
  } else {
    document.getElementById("course-title").value = "";
    document.getElementById("course-price").value = 0;
    document.getElementById("course-rating").value = 4.8;
    document.getElementById("course-thumbnail").value = "";
    document.getElementById("course-short-desc").value = "";
    document.getElementById("course-description").value = "";
    document.getElementById("instructor-name").value = "";
    document.getElementById("instructor-title").value = "";
    document.getElementById("course-featured").checked = false;
    title.textContent = "Add New Course";
  }

  if (modal) modal.classList.add("open");
}

function closeCourseModal() {
  const modal = document.getElementById("course-modal");
  if (modal) modal.classList.remove("open");
  editingCourseId = null;
}

async function saveCourse() {
  const saveBtn = document.getElementById("save-course-btn");
  const title = document.getElementById("course-title").value.trim();

  if (!title) {
    showToast("Validation Error", "Course title is required.", "warning");
    return;
  }

  const data = {
    title,
    category: document.getElementById("course-category").value,
    difficulty: document.getElementById("course-difficulty").value,
    price: parseFloat(document.getElementById("course-price").value) || 0,
    duration: document.getElementById("course-duration").value.trim() || "8h 00m",
    rating: parseFloat(document.getElementById("course-rating").value) || 4.8,
    thumbnail: document.getElementById("course-thumbnail").value.trim() || "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80",
    short_description: document.getElementById("course-short-desc").value.trim(),
    description: document.getElementById("course-description").value.trim(),
    featured: document.getElementById("course-featured").checked,
    instructor: {
      name: document.getElementById("instructor-name").value.trim() || "LearnHub Instructor",
      title: document.getElementById("instructor-title").value.trim() || "Senior Educator",
      avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(document.getElementById("instructor-name").value.trim() || "Instructor")}`,
      bio: "Expert instructor with years of practical teaching experience."
    }
  };

  saveBtn.disabled = true;
  saveBtn.innerHTML = `<span class="spinner"></span> Saving...`;

  let res;
  if (editingCourseId) {
    res = await apiRequest(`/api/courses/${editingCourseId}`, { method: "PUT", body: JSON.stringify(data) });
  } else {
    res = await apiRequest("/api/courses", { method: "POST", body: JSON.stringify(data) });
  }

  saveBtn.disabled = false;
  saveBtn.innerHTML = `<i class="fa-solid fa-floppy-disk"></i> Save Course`;

  if (res.ok && res.data.success) {
    showToast("Course Saved", editingCourseId ? "Course updated successfully." : "New course created!", "success");
    closeCourseModal();
    await loadAdminData();
  } else {
    showToast("Save Error", res.data.message || "Failed to save course.", "error");
  }
}

function confirmDeleteCourse(courseId, courseTitle) {
  const modal = document.getElementById("confirm-modal");
  const msg = document.getElementById("confirm-modal-msg");
  const btn = document.getElementById("confirm-delete-btn");
  if (msg) msg.textContent = `Are you sure you want to permanently delete "${courseTitle}"? All enrollments and progress data will be lost.`;
  if (btn) btn.onclick = () => deleteCourse(courseId);
  if (modal) modal.classList.add("open");
}

function closeConfirmModal() {
  const modal = document.getElementById("confirm-modal");
  if (modal) modal.classList.remove("open");
}

async function deleteCourse(courseId) {
  const res = await apiRequest(`/api/courses/${courseId}`, { method: "DELETE" });
  closeConfirmModal();
  if (res.ok && res.data.success) {
    showToast("Course Deleted", "The course has been permanently removed.", "success");
    await loadAdminData();
  } else {
    showToast("Delete Failed", res.data.message || "Unable to delete course.", "error");
  }
}
