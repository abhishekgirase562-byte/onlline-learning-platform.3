# LearnHub – Full-Stack Online Learning Platform

A complete, modern, production-ready Online Learning Platform built with **Python Flask**, **MongoDB**, and vanilla **HTML/CSS/JavaScript**.

---

## Live Demo Credentials

| Role    | Email                     | Password      |
|---------|---------------------------|---------------|
| Admin   | admin@learnhub.com        | Admin@12345   |
| Student | student@learnhub.com      | Student@12345 |
| Student | emma@learnhub.com         | Student@12345 |

---

## Features

- **Home Page** – Hero section, featured courses, category cards, testimonials, and CTA
- **Course Catalog** – Real-time search, category pill filters, difficulty and sort controls
- **Course Details** – Full curriculum, learning objectives, instructor profile, enrollment
- **Lesson Classroom** – HTML5 video player, sidebar navigation, lesson progress tracking
- **Student Dashboard** – Enrolled courses, progress bars, stats, and profile editing
- **Admin Console** – Course CRUD, lesson management, student roster, enrollment overview
- **Authentication** – Secure session-based login/register with Werkzeug password hashing
- **Role-Based Access** – Admin and Student roles with backend enforcement
- **mongomock Fallback** – Works without a live MongoDB installation for instant local testing

---

## Project Structure

```
online-learning-platform/
├── frontend/
│   ├── index.html              # Home page
│   ├── courses.html            # Course catalog
│   ├── course-details.html     # Course detail view
│   ├── login.html              # Login page
│   ├── register.html           # Registration page
│   ├── dashboard.html          # Student dashboard
│   ├── lesson.html             # Classroom / lesson player
│   ├── admin.html              # Admin console
│   ├── css/
│   │   └── style.css           # Full design system stylesheet
│   └── js/
│       ├── main.js             # API client, navbar, toast notifications
│       ├── auth.js             # Login / registration forms
│       ├── courses.js          # Catalog, search, course details, enrollment
│       ├── dashboard.js        # Student dashboard controller
│       ├── lesson.js           # Classroom / progress tracking controller
│       └── admin.js            # Admin dashboard controller
├── backend/
│   ├── app.py                  # Flask app factory with blueprints and static serving
│   ├── config.py               # Config + smart MongoDB/mongomock connection manager
│   ├── seed.py                 # Database seeder with 6 sample courses + users
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment variable template (copy to .env)
│   ├── models/
│   │   ├── user_model.py       # User CRUD and password hashing
│   │   ├── course_model.py     # Course CRUD with search/filter
│   │   ├── enrollment_model.py # Enrollment management
│   │   └── progress_model.py   # Lesson progress tracking
│   ├── routes/
│   │   ├── auth_routes.py      # /api/auth/*
│   │   ├── course_routes.py    # /api/courses/*
│   │   ├── enrollment_routes.py# /api/enrollments/*
│   │   ├── progress_routes.py  # /api/progress/*
│   │   └── admin_routes.py     # /api/admin/*
│   ├── services/
│   │   ├── auth_service.py     # Registration, login, session management
│   │   ├── course_service.py   # Course business logic + lesson access control
│   │   ├── enrollment_service.py# Enrollment + dashboard aggregations
│   │   ├── progress_service.py # Lesson completion business logic
│   │   └── admin_service.py    # Admin stats, students, enrollments
│   └── middleware/
│       └── auth_middleware.py  # login_required, admin_required decorators
└── tests/
    ├── conftest.py             # Pytest fixtures with isolated mongomock DB
    ├── test_auth.py            # Authentication tests (5 tests)
    ├── test_courses.py         # Course API tests (4 tests)
    ├── test_enrollment_and_progress.py  # Enrollment + progress tests (1 test)
    └── test_admin.py           # Admin access + CRUD tests (3 tests)
```

---

## Quick Start

### 1. Prerequisites

- Python 3.9+ (tested on 3.13)
- pip
- MongoDB (optional — falls back to in-memory `mongomock` automatically)

### 2. Setup & Run

```bash
# Clone or navigate to project directory
cd online-learning-platform

# Install Python dependencies
pip install -r backend/requirements.txt

# (Optional) Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your MongoDB URI if available

# Run the Flask application (auto-seeds sample data on first run)
python backend/app.py
```

Open your browser at: **http://localhost:5000**

### 3. Run Tests

```bash
cd online-learning-platform
pytest -v
```

All 13 tests pass using in-memory `mongomock` — no MongoDB installation required.

---

## MongoDB Setup (Optional)

The platform works **out of the box** without MongoDB by automatically falling back to `mongomock` (an in-memory MongoDB emulator).

To use a real MongoDB database:

1. Install MongoDB: https://www.mongodb.com/try/download/community
2. Start the service: `mongod --dbpath ./data/db`
3. Update `backend/.env`:
   ```
   MONGO_URI=mongodb://localhost:27017/learnhub
   ```
4. (Optional) Re-run the seed to populate the database:
   ```bash
   python backend/seed.py
   ```

To use MongoDB Atlas (cloud):
```
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/learnhub
```

---

## API Endpoints

### Authentication
| Method | Endpoint              | Description                  |
|--------|-----------------------|------------------------------|
| POST   | /api/auth/register    | Create new account           |
| POST   | /api/auth/login       | Login and create session      |
| POST   | /api/auth/logout      | Destroy session              |
| GET    | /api/auth/me          | Get current user info        |
| PUT    | /api/auth/profile     | Update profile (auth req.)   |

### Courses
| Method | Endpoint                                    | Description                         |
|--------|---------------------------------------------|-------------------------------------|
| GET    | /api/courses                                | List/search/filter courses          |
| GET    | /api/courses/:id                            | Course details + lesson access guard|
| POST   | /api/courses                                | Create course (admin only)          |
| PUT    | /api/courses/:id                            | Update course (admin only)          |
| DELETE | /api/courses/:id                            | Delete course (admin only)          |
| POST   | /api/courses/:id/lessons                    | Add lesson (admin only)             |
| PUT    | /api/courses/:id/lessons/:lesson_id         | Update lesson (admin only)          |
| DELETE | /api/courses/:id/lessons/:lesson_id         | Delete lesson (admin only)          |

### Enrollments & Progress
| Method | Endpoint                                         | Description                    |
|--------|--------------------------------------------------|--------------------------------|
| POST   | /api/enrollments/:course_id                      | Enroll in course               |
| GET    | /api/enrollments/my-courses                      | Get student dashboard data     |
| GET    | /api/enrollments/:course_id/status               | Check enrollment status        |
| GET    | /api/progress/:course_id                         | Get progress for a course      |
| POST   | /api/progress/:course_id/lessons/:id/complete    | Mark lesson completed          |
| POST   | /api/progress/:course_id/lessons/:id/uncomplete  | Mark lesson incomplete         |

### Admin
| Method | Endpoint             | Description                 |
|--------|----------------------|-----------------------------|
| GET    | /api/admin/stats     | Platform-wide statistics    |
| GET    | /api/admin/students  | All registered students     |
| GET    | /api/admin/enrollments| All enrollments with details|

---

## Security

- Passwords are hashed with **Werkzeug PBKDF2** — never stored in plaintext
- Session cookies are **HttpOnly** and **SameSite=Lax**
- All admin endpoints are protected by the `@admin_required` decorator
- CORS is configured to only allow specific origins
- Server-side validation on all user inputs

---

## Sample Data

The seed script creates:
- **6 courses** across Web Dev, Data Science, UI/UX, DevOps, Cybersecurity, and Mobile Dev
- **3 users** (1 admin, 2 students)
- **3 enrollments** with lesson progress pre-populated for demo

Sample video content uses freely available MP4 files from Google's public CDN.
