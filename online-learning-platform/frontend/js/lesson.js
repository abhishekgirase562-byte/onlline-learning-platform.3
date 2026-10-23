/**
 * LearnHub - Lesson / Classroom Controller
 */

let currentCourse = null;
let currentLesson = null;

document.addEventListener("DOMContentLoaded", () => {
  initClassroom();
});

async function initClassroom() {
  const root = document.getElementById("classroom-root");
  if (!root) return;

  // Verify authentication
  const authRes = await apiRequest("/api/auth/me");
  if (!authRes.ok || !authRes.data.authenticated) {
    showToast("Authentication Required", "Please log in to access the classroom.", "warning");
    setTimeout(() => { window.location.href = "login.html?redirect=" + encodeURIComponent(window.location.href); }, 800);
    return;
  }

  const user = authRes.data.user;
  const urlParams = new URLSearchParams(window.location.search);
  const courseId = urlParams.get("course_id");
  const requestedLessonId = urlParams.get("lesson_id");

  if (!courseId) {
    root.innerHTML = `<div class="empty-state container"><h3>No Course Selected</h3><a href="courses.html" class="btn btn-primary" style="margin-top:1rem;">Browse Courses</a></div>`;
    return;
  }

  root.innerHTML = `<div style="text-align:center;padding:6rem 0;"><div class="spinner spinner-primary"></div><p style="margin-top:1rem;color:var(--text-muted);">Loading classroom...</p></div>`;

  const res = await apiRequest(`/api/courses/${courseId}`);
  if (!res.ok || !res.data.success) {
    root.innerHTML = `<div class="empty-state container"><h3>Unable to load course</h3><a href="courses.html" class="btn btn-primary" style="margin-top:1rem;">Browse Courses</a></div>`;
    return;
  }

  currentCourse = res.data.course;
  const lessons = currentCourse.lessons || [];
  const isEnrolled = currentCourse.is_enrolled || user.role === "admin";

  if (!isEnrolled) {
    root.innerHTML = `
      <div class="empty-state container" style="padding: 6rem 0;">
        <i class="fa-solid fa-lock empty-state-icon" style="color: var(--secondary);"></i>
        <h2>Enrollment Required</h2>
        <p style="color: var(--text-muted); max-width: 420px; margin: 0.5rem auto 1.5rem;">Please enroll in this course to access lessons and video content.</p>
        <div style="display:flex;gap:1rem;justify-content:center;">
          <a href="course-details.html?id=${courseId}" class="btn btn-primary">
            <i class="fa-solid fa-graduation-cap"></i> Enroll Now
          </a>
          <a href="courses.html" class="btn btn-outline">Browse Other Courses</a>
        </div>
      </div>
    `;
    return;
  }

  // Load progress
  const progressRes = await apiRequest(`/api/progress/${courseId}`);
  const progress = progressRes.ok ? (progressRes.data.progress || {}) : {};
  const completedLessons = new Set(progress.completed_lessons || []);

  // Determine lesson to show
  let activeLesson = lessons.find(l => l.id === requestedLessonId) || lessons[0];
  currentLesson = activeLesson;

  function buildSidebar() {
    return lessons.map((lesson, idx) => {
      const isActive = lesson.id === currentLesson?.id;
      const isDone = completedLessons.has(lesson.id);
      const isLocked = lesson.is_locked && !isEnrolled;
      return `
        <div class="sidebar-lesson-item ${isActive ? 'active' : ''}" 
             onclick="${isLocked ? '' : `loadLesson('${lesson.id}')`}"
             id="sidebar-item-${lesson.id}"
             style="${isLocked ? 'opacity:0.5;cursor:not-allowed;' : 'cursor:pointer;'}">
          <div class="lesson-check-icon ${isDone ? 'completed' : ''}">
            ${isDone ? '<i class="fa-solid fa-circle-check"></i>' : `<i class="fa-regular fa-circle" style="color:var(--text-light);"></i>`}
          </div>
          <div style="flex:1; min-width:0;">
            <div class="lesson-title-text" style="font-size:0.88rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${lesson.title}</div>
            <div style="font-size:0.75rem; color:var(--text-muted);">${lesson.duration || '10:00'}</div>
          </div>
          ${isLocked ? '<i class="fa-solid fa-lock" style="color:var(--text-light);font-size:0.8rem;"></i>' : ''}
        </div>
      `;
    }).join('');
  }

  function buildClassroomHTML(lesson) {
    const lessonIdx = lessons.findIndex(l => l.id === lesson.id);
    const prevLesson = lessonIdx > 0 ? lessons[lessonIdx - 1] : null;
    const nextLesson = lessonIdx < lessons.length - 1 ? lessons[lessonIdx + 1] : null;
    const isDone = completedLessons.has(lesson.id);
    const completedCount = completedLessons.size;
    const totalCount = lessons.length;
    const progressPct = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

    return `
      <div class="classroom-layout">
        <!-- Main Video Area -->
        <div class="classroom-main">
          <div class="video-container">
            ${lesson.video_url ? `
              <video id="lesson-video" controls autoplay preload="metadata" style="width:100%;height:100%;">
                <source src="${lesson.video_url}" type="video/mp4" />
                <p style="color:#fff;padding:2rem;">Your browser does not support HTML5 video.</p>
              </video>
            ` : `
              <div style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;background:#1e293b;color:#64748b;flex-direction:column;gap:1rem;">
                <i class="fa-solid fa-lock" style="font-size:3rem;"></i>
                <p>Video requires enrollment access</p>
              </div>
            `}
          </div>

          <!-- Actions Bar -->
          <div class="classroom-actions">
            <div style="display:flex;align-items:center;gap:1rem;">
              ${prevLesson ? `
                <button class="btn btn-outline btn-sm" onclick="loadLesson('${prevLesson.id}')">
                  <i class="fa-solid fa-chevron-left"></i> Previous
                </button>
              ` : '<div></div>'}
              <span style="font-size:0.9rem;color:var(--text-muted);">Lesson ${lessonIdx + 1} of ${totalCount}</span>
              ${nextLesson ? `
                <button class="btn btn-primary btn-sm" onclick="loadLesson('${nextLesson.id}')">
                  Next <i class="fa-solid fa-chevron-right"></i>
                </button>
              ` : `
                <button class="btn btn-sm" style="background:var(--success);color:#fff;" onclick="loadLesson('${lesson.id}')">
                  <i class="fa-solid fa-trophy"></i> Course Complete!
                </button>
              `}
            </div>

            <button id="complete-toggle-btn"
              onclick="toggleLessonComplete('${lesson.id}', ${!isDone})"
              class="btn ${isDone ? 'btn-outline' : 'btn-secondary'} btn-sm">
              ${isDone ? '<i class="fa-solid fa-rotate-left"></i> Mark Incomplete' : '<i class="fa-solid fa-check"></i> Mark as Completed'}
            </button>
          </div>

          <!-- Lesson Info -->
          <div class="classroom-content">
            <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;flex-wrap:wrap;margin-bottom:1.25rem;">
              <div>
                <h1 style="font-size:1.6rem;margin-bottom:0.4rem;">${lesson.title}</h1>
                <p style="color:var(--text-muted);font-size:0.95rem;">${lesson.description || ''}</p>
              </div>
              ${isDone ? `<span class="badge badge-success"><i class="fa-solid fa-check"></i> Completed</span>` : ''}
            </div>

            <div style="padding:1.25rem;background:var(--bg-alt);border-radius:var(--radius-md);display:flex;align-items:center;gap:1.25rem;flex-wrap:wrap;">
              <div style="flex:1;">
                <div style="display:flex;justify-content:space-between;font-size:0.85rem;font-weight:600;margin-bottom:0.4rem;">
                  <span>Your Overall Progress</span>
                  <span style="color:var(--primary);">${completedCount} / ${totalCount} lessons (${progressPct}%)</span>
                </div>
                <div class="progress-bar-wrap"><div class="progress-bar-fill" style="width:${progressPct}%;"></div></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar Lesson Navigator -->
        <div class="classroom-sidebar">
          <div class="sidebar-header">
            <h3 style="font-size:1rem;margin-bottom:0.3rem;">${currentCourse.title}</h3>
            <div style="font-size:0.8rem;color:var(--text-muted);">${completedCount}/${totalCount} lessons completed</div>
          </div>
          <div class="sidebar-lessons" id="classroom-sidebar-lessons">
            ${buildSidebar()}
          </div>
        </div>
      </div>
    `;
  }

  root.innerHTML = buildClassroomHTML(activeLesson);

  window.loadLesson = async function(lessonId) {
    const lesson = lessons.find(l => l.id === lessonId);
    if (!lesson) return;
    currentLesson = lesson;

    // Update URL without reload
    const newUrl = new URL(window.location.href);
    newUrl.searchParams.set("lesson_id", lessonId);
    window.history.pushState({}, '', newUrl.toString());

    root.innerHTML = buildClassroomHTML(lesson);
  };

  window.toggleLessonComplete = async function(lessonId, markComplete) {
    const endpoint = markComplete
      ? `/api/progress/${courseId}/lessons/${lessonId}/complete`
      : `/api/progress/${courseId}/lessons/${lessonId}/uncomplete`;

    const res = await apiRequest(endpoint, { method: "POST" });
    if (res.ok && res.data.success) {
      const prog = res.data.progress;
      completedLessons.clear();
      (prog.completed_lessons || []).forEach(id => completedLessons.add(id));
      showToast(
        markComplete ? "Lesson Completed!" : "Marked Incomplete",
        markComplete ? `Great work! Progress: ${prog.progress_percentage}%` : "Lesson marked as incomplete.",
        markComplete ? "success" : "info"
      );
      // Re-render the classroom to reflect new state
      root.innerHTML = buildClassroomHTML(currentLesson);
    } else {
      showToast("Error", res.data.message || "Failed to update lesson progress.", "error");
    }
  };
}
