/**
 * LearnHub - Courses Management (Catalog & Details)
 */

document.addEventListener("DOMContentLoaded", () => {
  // If on index.html
  if (document.getElementById("featured-courses-grid")) {
    loadFeaturedCourses();
  }

  // If on courses.html
  if (document.getElementById("courses-catalog-grid")) {
    initCoursesCatalog();
  }

  // If on course-details.html
  if (document.getElementById("course-details-root")) {
    initCourseDetails();
  }
});

/**
 * Render standard reusable course card HTML
 */
function createCourseCardHTML(course) {
  const category = course.category || "General";
  const difficulty = course.difficulty || "Beginner";
  const instructor = course.instructor || { name: "LearnHub Educator", avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Teacher" };
  const rating = course.rating || 4.8;
  const reviewsCount = course.reviews_count || 0;
  const lessonsCount = course.lessons ? course.lessons.length : 0;
  const isEnrolled = course.is_enrolled || false;

  return `
    <div class="course-card">
      <div class="card-thumbnail-wrap">
        <img src="${course.thumbnail || 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80'}" alt="${course.title}" loading="lazy" />
        <span class="card-category-badge">${category}</span>
        ${course.featured ? `<span class="badge badge-featured card-featured-badge"><i class="fa-solid fa-bolt"></i> Featured</span>` : ''}
      </div>

      <div class="card-content">
        <div class="card-meta">
          <span><i class="fa-solid fa-signal" style="color: var(--primary);"></i> ${difficulty}</span>
          <span><i class="fa-regular fa-clock"></i> ${course.duration || '6h 00m'}</span>
          <span><i class="fa-solid fa-play" style="font-size: 0.75rem;"></i> ${lessonsCount} Lessons</span>
        </div>

        <h3 class="card-title">
          <a href="course-details.html?id=${course.id}">${course.title}</a>
        </h3>

        <p class="card-desc">${course.short_description || course.description || ''}</p>

        <div class="card-instructor">
          <img src="${instructor.avatar}" alt="${instructor.name}" />
          <div class="inst-info">
            <div class="inst-name">${instructor.name}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">${instructor.title || 'Lead Instructor'}</div>
          </div>
        </div>

        <div class="card-footer">
          <div class="card-price">${formatPrice(course.price)}</div>
          <div class="card-rating">
            ${renderRatingStars(rating)}
            <span style="font-size: 0.75rem; color: var(--text-muted);">(${reviewsCount})</span>
          </div>
        </div>

        <div style="margin-top: 1.25rem;">
          <a href="course-details.html?id=${course.id}" class="btn btn-outline-primary btn-block btn-sm">
            ${isEnrolled ? '<i class="fa-solid fa-circle-play"></i> Continue Course' : 'View Course Details'}
          </a>
        </div>
      </div>
    </div>
  `;
}

/**
 * Load featured courses for Home Page
 */
async function loadFeaturedCourses() {
  const container = document.getElementById("featured-courses-grid");
  if (!container) return;

  container.innerHTML = `
    <div style="grid-column: 1 / -1; text-align: center; padding: 3rem;">
      <div class="spinner spinner-primary"></div>
      <p style="margin-top: 1rem; color: var(--text-muted);">Loading popular courses...</p>
    </div>
  `;

  const res = await apiRequest("/api/courses?featured=true&limit=3");
  if (res.ok && res.data.success && res.data.courses.length > 0) {
    container.innerHTML = res.data.courses.map(createCourseCardHTML).join("");
  } else {
    // If no featured, fetch any 3 courses
    const fallbackRes = await apiRequest("/api/courses?limit=3");
    if (fallbackRes.ok && fallbackRes.data.courses.length > 0) {
      container.innerHTML = fallbackRes.data.courses.map(createCourseCardHTML).join("");
    } else {
      container.innerHTML = `<p style="grid-column: 1 / -1; text-align: center; color: var(--text-muted);">No courses available yet.</p>`;
    }
  }
}

/**
 * Catalog Page Interactive Controller (Search, Filter, Sort)
 */
function initCoursesCatalog() {
  const container = document.getElementById("courses-catalog-grid");
  const searchInput = document.getElementById("catalog-search");
  const categoryPills = document.querySelectorAll(".category-pills .pill-btn");
  const difficultySelect = document.getElementById("filter-difficulty");
  const sortSelect = document.getElementById("filter-sort");
  const resultsCount = document.getElementById("results-count");

  let currentCategory = "all";
  let searchDebounceTimer = null;

  async function fetchAndRender() {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 4rem;">
        <div class="spinner spinner-primary"></div>
        <p style="margin-top: 1rem; color: var(--text-muted);">Finding matching courses...</p>
      </div>
    `;

    const searchVal = searchInput ? searchInput.value.trim() : "";
    const diffVal = difficultySelect ? difficultySelect.value : "all";
    const sortVal = sortSelect ? sortSelect.value : "";

    const params = new URLSearchParams();
    if (searchVal) params.append("search", searchVal);
    if (currentCategory && currentCategory !== "all") params.append("category", currentCategory);
    if (diffVal && diffVal !== "all") params.append("difficulty", diffVal);
    if (sortVal) params.append("sort_by", sortVal);

    const res = await apiRequest(`/api/courses?${params.toString()}`);

    if (res.ok && res.data.success) {
      const courses = res.data.courses || [];
      if (resultsCount) {
        resultsCount.textContent = `Showing ${courses.length} ${courses.length === 1 ? 'course' : 'courses'}`;
      }

      if (courses.length === 0) {
        container.innerHTML = `
          <div style="grid-column: 1 / -1;" class="empty-state">
            <i class="fa-solid fa-magnifying-glass empty-state-icon"></i>
            <h3>No matching courses found</h3>
            <p style="color: var(--text-muted); margin-top: 0.5rem;">Try adjusting your search terms or clearing your filters.</p>
            <button class="btn btn-outline-primary" style="margin-top: 1.5rem;" onclick="resetCatalogFilters()">
              Clear All Filters
            </button>
          </div>
        `;
      } else {
        container.innerHTML = courses.map(createCourseCardHTML).join("");
      }
    } else {
      container.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--danger);">
          <i class="fa-solid fa-triangle-exclamation" style="font-size: 2rem; margin-bottom: 1rem;"></i>
          <p>Failed to load courses. Please make sure the backend server is running.</p>
        </div>
      `;
    }
  }

  window.resetCatalogFilters = () => {
    if (searchInput) searchInput.value = "";
    if (difficultySelect) difficultySelect.value = "all";
    if (sortSelect) sortSelect.value = "featured";
    currentCategory = "all";
    categoryPills.forEach(p => p.classList.remove("active"));
    const allPill = document.querySelector('.pill-btn[data-category="all"]');
    if (allPill) allPill.classList.add("active");
    fetchAndRender();
  };

  // Search input with 300ms debounce
  if (searchInput) {
    searchInput.addEventListener("input", () => {
      clearTimeout(searchDebounceTimer);
      searchDebounceTimer = setTimeout(fetchAndRender, 300);
    });
  }

  // Category pill selection
  categoryPills.forEach(pill => {
    pill.addEventListener("click", () => {
      categoryPills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      currentCategory = pill.dataset.category || "all";
      fetchAndRender();
    });
  });

  // Difficulty & Sort changes
  if (difficultySelect) difficultySelect.addEventListener("change", fetchAndRender);
  if (sortSelect) sortSelect.addEventListener("change", fetchAndRender);

  // Check URL query parameters for initial filters (e.g., ?category=Web%20Development)
  const urlParams = new URLSearchParams(window.location.search);
  const initialCat = urlParams.get("category");
  if (initialCat) {
    currentCategory = initialCat;
    categoryPills.forEach(p => {
      if (p.dataset.category && p.dataset.category.toLowerCase() === initialCat.toLowerCase()) {
        p.classList.add("active");
      } else {
        p.classList.remove("active");
      }
    });
  }

  const initialSearch = urlParams.get("search");
  if (initialSearch && searchInput) {
    searchInput.value = initialSearch;
  }

  // Initial load
  fetchAndRender();
}

/**
 * Course Details Page Controller
 */
async function initCourseDetails() {
  const root = document.getElementById("course-details-root");
  if (!root) return;

  const urlParams = new URLSearchParams(window.location.search);
  const courseId = urlParams.get("id");

  if (!courseId) {
    root.innerHTML = `
      <div class="empty-state container">
        <i class="fa-solid fa-circle-exclamation empty-state-icon" style="color: var(--danger);"></i>
        <h2>Course Not Found</h2>
        <p style="color: var(--text-muted); margin-top: 0.5rem;">No course ID was provided.</p>
        <a href="courses.html" class="btn btn-primary" style="margin-top: 1.5rem;">Browse Courses</a>
      </div>
    `;
    return;
  }

  root.innerHTML = `
    <div style="text-align: center; padding: 6rem 0;">
      <div class="spinner spinner-primary"></div>
      <p style="margin-top: 1rem; color: var(--text-muted);">Loading course details...</p>
    </div>
  `;

  const res = await apiRequest(`/api/courses/${courseId}`);

  if (!res.ok || !res.data.success || !res.data.course) {
    root.innerHTML = `
      <div class="empty-state container">
        <i class="fa-solid fa-triangle-exclamation empty-state-icon" style="color: var(--danger);"></i>
        <h2>Unable to load course</h2>
        <p style="color: var(--text-muted); margin-top: 0.5rem;">${res.data.message || 'Course does not exist or was removed.'}</p>
        <a href="courses.html" class="btn btn-primary" style="margin-top: 1.5rem;">Back to Catalog</a>
      </div>
    `;
    return;
  }

  const course = res.data.course;
  const isEnrolled = course.is_enrolled || false;
  const lessons = course.lessons || [];
  const instructor = course.instructor || {
    name: "Dr. Alexander Wright",
    title: "Senior Curriculum Architect",
    avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&q=80",
    bio: "Passionate software engineer and tech educator with over 15 years of industry experience."
  };

  root.innerHTML = `
    <!-- Hero Banner -->
    <section class="course-hero-banner">
      <div class="container course-hero-grid">
        <div class="course-hero-info">
          <div style="display: flex; gap: 0.75rem; margin-bottom: 1rem;">
            <span class="badge badge-primary">${course.category || 'General'}</span>
            <span class="badge" style="background: rgba(255,255,255,0.15); color: #fff;">${course.difficulty || 'Beginner'}</span>
          </div>

          <h1>${course.title}</h1>
          <p class="course-hero-subtitle">${course.short_description || course.description || ''}</p>

          <div class="course-hero-meta">
            <span><i class="fa-solid fa-user-tie"></i> Created by <strong>${instructor.name}</strong></span>
            <span><i class="fa-solid fa-clock"></i> ${course.duration || '12h 00m'}</span>
            <span><i class="fa-solid fa-play"></i> ${lessons.length} Lessons</span>
            <span><i class="fa-solid fa-users"></i> ${course.students_enrolled || 0} Students</span>
            <span>${renderRatingStars(course.rating || 4.8)} (${course.reviews_count || 0})</span>
          </div>
        </div>

        <!-- Sticky Enrollment Card -->
        <div class="enrollment-card">
          <div class="enroll-thumbnail-wrap">
            <img src="${course.thumbnail}" alt="${course.title}" />
          </div>

          <div class="enroll-body">
            <div class="enroll-price-box">
              <span class="enroll-price">${formatPrice(course.price)}</span>
              ${course.price > 0 ? `<span style="text-decoration: line-through; color: var(--text-light); font-size: 1.1rem;">$${(course.price * 1.5).toFixed(2)}</span>` : ''}
            </div>

            <div id="enroll-action-container">
              ${isEnrolled ? `
                <a href="lesson.html?course_id=${course.id}&lesson_id=${lessons[0] ? lessons[0].id : ''}" class="btn btn-success btn-block btn-lg">
                  <i class="fa-solid fa-circle-play"></i> Go to Classroom
                </a>
                <p style="text-align: center; color: var(--success); font-size: 0.85rem; margin-top: 0.6rem; font-weight: 600;">
                  <i class="fa-solid fa-check-circle"></i> You are enrolled in this course
                </p>
              ` : `
                <button onclick="handleEnroll('${course.id}')" id="enroll-submit-btn" class="btn btn-primary btn-block btn-lg">
                  <i class="fa-solid fa-graduation-cap"></i> Enroll Now
                </button>
                <p style="text-align: center; color: var(--text-muted); font-size: 0.8rem; margin-top: 0.6rem;">
                  30-Day Money-Back Guarantee • Lifetime Access
                </p>
              `}
            </div>

            <ul class="course-includes">
              <li style="font-weight: 700; color: var(--text-main); margin-bottom: 1rem;">This course includes:</li>
              <li><i class="fa-solid fa-video"></i> ${course.duration || '12+ hours'} on-demand video</li>
              <li><i class="fa-solid fa-file-code"></i> Full downloadable source code & assets</li>
              <li><i class="fa-solid fa-mobile-screen"></i> Accessible on mobile and desktop</li>
              <li><i class="fa-solid fa-infinity"></i> Full lifetime access</li>
              <li><i class="fa-solid fa-certificate"></i> Certificate of completion</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- Content Sections -->
    <section class="section">
      <div class="container" style="display: grid; grid-template-columns: 1.3fr 0.7fr; gap: 3.5rem;">
        <div>
          <!-- What You'll Learn -->
          ${course.learning_objectives && course.learning_objectives.length > 0 ? `
            <div style="background: #fff; padding: 2rem; border-radius: var(--radius-lg); border: 1px solid var(--border); margin-bottom: 2.5rem;">
              <h2 style="font-size: 1.4rem; margin-bottom: 1.25rem;">What you will learn</h2>
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                ${course.learning_objectives.map(obj => `
                  <div style="display: flex; align-items: flex-start; gap: 0.6rem; font-size: 0.95rem;">
                    <i class="fa-solid fa-circle-check" style="color: var(--success); margin-top: 3px;"></i>
                    <span>${obj}</span>
                  </div>
                `).join('')}
              </div>
            </div>
          ` : ''}

          <!-- Curriculum -->
          <div style="margin-bottom: 2.5rem;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
              <h2 style="font-size: 1.4rem;">Course Curriculum</h2>
              <span style="font-size: 0.9rem; color: var(--text-muted);">${lessons.length} lessons • ${course.duration || ''}</span>
            </div>

            <div class="curriculum-list">
              ${lessons.map((lesson, idx) => `
                <div class="curriculum-item">
                  <div class="lesson-left">
                    <div class="lesson-order">${idx + 1}</div>
                    <div>
                      <div class="lesson-title-text">${lesson.title}</div>
                      ${lesson.description ? `<div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.2rem;">${lesson.description}</div>` : ''}
                    </div>
                  </div>

                  <div class="lesson-right">
                    ${lesson.is_preview ? `
                      <a href="lesson.html?course_id=${course.id}&lesson_id=${lesson.id}" class="badge badge-primary" style="text-decoration: none;">
                        <i class="fa-solid fa-play"></i> Preview
                      </a>
                    ` : isEnrolled ? `
                      <a href="lesson.html?course_id=${course.id}&lesson_id=${lesson.id}" class="badge badge-success" style="text-decoration: none;">
                        <i class="fa-solid fa-play"></i> Play
                      </a>
                    ` : `
                      <span class="badge" style="background: var(--bg-alt); color: var(--text-light);">
                        <i class="fa-solid fa-lock"></i> Protected
                      </span>
                    `}
                    <span>${lesson.duration || '10:00'}</span>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>

          <!-- Requirements -->
          ${course.requirements && course.requirements.length > 0 ? `
            <div style="margin-bottom: 2.5rem;">
              <h2 style="font-size: 1.4rem; margin-bottom: 1rem;">Requirements</h2>
              <ul style="padding-left: 1.5rem; color: var(--text-muted); font-size: 0.95rem; display: flex; flex-direction: column; gap: 0.5rem;">
                ${course.requirements.map(req => `<li>${req}</li>`).join('')}
              </ul>
            </div>
          ` : ''}

          <!-- Course Description -->
          <div style="margin-bottom: 2.5rem;">
            <h2 style="font-size: 1.4rem; margin-bottom: 1rem;">Full Course Description</h2>
            <div style="color: var(--text-main); font-size: 1rem; line-height: 1.7; white-space: pre-line;">
              ${course.description || course.short_description || 'Detailed course contents provided by instructor.'}
            </div>
          </div>

          <!-- Instructor Information -->
          <div style="background: #fff; padding: 2rem; border-radius: var(--radius-lg); border: 1px solid var(--border);">
            <h2 style="font-size: 1.4rem; margin-bottom: 1.25rem;">Your Instructor</h2>
            <div style="display: flex; gap: 1.5rem; align-items: flex-start;">
              <img src="${instructor.avatar}" alt="${instructor.name}" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover;" />
              <div>
                <h3 style="font-size: 1.15rem; margin-bottom: 0.2rem;">${instructor.name}</h3>
                <div style="color: var(--primary); font-size: 0.9rem; font-weight: 600; margin-bottom: 0.75rem;">${instructor.title || 'Lead Instructor'}</div>
                <p style="color: var(--text-muted); font-size: 0.9rem; line-height: 1.6;">${instructor.bio || ''}</p>
              </div>
            </div>
          </div>
        </div>

        <div><!-- Spacer to balance grid against sticky right card --></div>
      </div>
    </section>
  `;
}

/**
 * Handle student enrollment in course
 */
async function handleEnroll(courseId) {
  // Check if logged in
  if (!window.currentUser) {
    showToast("Authentication Required", "Please log in or create an account to enroll.", "warning");
    setTimeout(() => {
      window.location.href = `login.html?redirect=${encodeURIComponent(window.location.href)}`;
    }, 1200);
    return;
  }

  const btn = document.getElementById("enroll-submit-btn");
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> Processing Enrollment...`;
  }

  const res = await apiRequest(`/api/enrollments/${courseId}`, { method: "POST" });

  if (res.ok && res.data.success) {
    showToast("Success!", res.data.message || "Successfully enrolled in this course!", "success");
    setTimeout(() => {
      window.location.href = `lesson.html?course_id=${courseId}`;
    }, 900);
  } else {
    showToast("Enrollment Failed", res.data.message || "Could not complete enrollment.", "error");
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<i class="fa-solid fa-graduation-cap"></i> Enroll Now`;
    }
  }
}
