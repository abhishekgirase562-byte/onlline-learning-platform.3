import os
import sys

# Ensure backend package can be imported
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.config import init_db, get_db
from backend.models.user_model import UserModel
from backend.models.course_model import CourseModel
from backend.models.enrollment_model import EnrollmentModel
from backend.models.progress_model import ProgressModel

# Video sample URLs for high reliability and smooth in-browser playback
SAMPLE_VIDEOS = [
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4"
]

def seed_database(quiet=False):
    db = get_db()
    if not quiet:
        print("[LearnHub Seed] Clearing existing data for fresh seed...")
    db["users"].delete_many({})
    db["courses"].delete_many({})
    db["enrollments"].delete_many({})
    db["lesson_progress"].delete_many({})

    if not quiet:
        print("[LearnHub Seed] Creating admin and student users...")
    # Admin User
    admin_user, _ = UserModel.create_user(
        name="Dr. Alexander Wright",
        email="admin@learnhub.com",
        password="Admin@12345",
        role="admin",
        bio="Lead Architect & Head of Curriculum at LearnHub. 15+ years in full-stack architecture.",
        avatar="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&q=80"
    )

    # Demo Student User
    student_user, _ = UserModel.create_user(
        name="Sarah Connor",
        email="student@learnhub.com",
        password="Student@12345",
        role="student",
        bio="Passionate aspiring full-stack engineer and lifelong tech learner.",
        avatar="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&q=80"
    )

    # Secondary Student User
    student_user_2, _ = UserModel.create_user(
        name="Emma Watson",
        email="emma@learnhub.com",
        password="Student@12345",
        role="student",
        bio="Data analytics enthusiast exploring machine learning models.",
        avatar="https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&q=80"
    )

    if not quiet:
        print("[LearnHub Seed] Creating educational courses and curriculum...")

    courses_data = [
        {
            "title": "Modern Full-Stack Web Development: From Zero to Hero",
            "slug": "modern-full-stack-web-development",
            "category": "Web Development",
            "difficulty": "Beginner",
            "duration": "18h 30m",
            "price": 49.99,
            "featured": True,
            "rating": 4.9,
            "reviews_count": 3420,
            "students_enrolled": 12850,
            "thumbnail": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800&q=80",
            "short_description": "Master HTML5, modern CSS, modern JavaScript, Flask backends, REST APIs, and production deployment.",
            "description": "Step into modern web engineering. In this comprehensive bootcamp, you will build full-stack web applications from absolute scratch. Learn modern semantic markup, responsive layout engines with Flexbox and CSS Grid, asynchronous JavaScript with Fetch and REST APIs, session-based authentication, and Python Flask architectures.",
            "learning_objectives": [
                "Build modern, mobile-first responsive web apps with semantic HTML5 and CSS3",
                "Master asynchronous JavaScript, DOM manipulation, and JSON API communications",
                "Architect robust RESTful APIs in Python Flask with session authentication",
                "Integrate MongoDB collections with PyMongo for flexible persistence",
                "Implement secure password hashing, CSRF defenses, and role-based permissions"
            ],
            "requirements": [
                "Basic computer literacy and a text editor or IDE",
                "No prior programming experience required; we start from ground zero"
            ],
            "instructor": {
                "name": "Dr. Alexander Wright",
                "title": "Principal Software Architect",
                "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&q=80",
                "bio": "15+ years architecting distributed systems and educating thousands of software engineers."
            },
            "lessons": [
                {
                    "id": "lesson-101",
                    "title": "Introduction to Modern Web Architecture",
                    "description": "Understand client-server architecture, HTTP request-response lifecycles, and modern developer tooling.",
                    "duration": "14:20",
                    "video_url": SAMPLE_VIDEOS[0],
                    "order": 1,
                    "is_preview": True
                },
                {
                    "id": "lesson-102",
                    "title": "Semantic HTML5 and Modern CSS Layouts",
                    "description": "Master Flexbox, CSS Grid, custom properties, and responsive media queries without external bloat.",
                    "duration": "22:15",
                    "video_url": SAMPLE_VIDEOS[1],
                    "order": 2,
                    "is_preview": True
                },
                {
                    "id": "lesson-103",
                    "title": "JavaScript ES6+ Deep Dive & Asynchronous Programming",
                    "description": "Promises, async/await, Fetch API, closures, modules, and modern browser storage engines.",
                    "duration": "28:40",
                    "video_url": SAMPLE_VIDEOS[2],
                    "order": 3,
                    "is_preview": False
                },
                {
                    "id": "lesson-104",
                    "title": "Building REST APIs with Python Flask",
                    "description": "Route controllers, JSON serialization, HTTP status codes, and modular blueprint architecture.",
                    "duration": "31:10",
                    "video_url": SAMPLE_VIDEOS[3],
                    "order": 4,
                    "is_preview": False
                },
                {
                    "id": "lesson-105",
                    "title": "MongoDB Integration & Data Modeling with PyMongo",
                    "description": "Designing document collections, indexing, CRUD pipelines, and relationship referencing.",
                    "duration": "25:45",
                    "video_url": SAMPLE_VIDEOS[4],
                    "order": 5,
                    "is_preview": False
                },
                {
                    "id": "lesson-106",
                    "title": "Security, Password Hashing & Role-Based Access Control",
                    "description": "Secure cookie sessions, Werkzeug password hashing, authorization gates, and vulnerability mitigations.",
                    "duration": "24:18",
                    "video_url": SAMPLE_VIDEOS[5],
                    "order": 6,
                    "is_preview": False
                }
            ]
        },
        {
            "title": "Python for Data Science and Machine Learning",
            "slug": "python-data-science-machine-learning",
            "category": "Data Science",
            "difficulty": "Intermediate",
            "duration": "22h 15m",
            "price": 59.99,
            "featured": True,
            "rating": 4.8,
            "reviews_count": 2180,
            "students_enrolled": 9740,
            "thumbnail": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80",
            "short_description": "Harness NumPy, Pandas, Scikit-Learn, data visualization, and applied machine learning models.",
            "description": "Dive deep into data analysis and statistical modeling. Learn how to clean raw datasets, engineer impactful features, train predictive models, and evaluate algorithm performance using real industry data.",
            "learning_objectives": [
                "Manipulate complex tabular datasets with high efficiency using Pandas and NumPy",
                "Create publication-grade exploratory data visualizations",
                "Train supervised regression and classification models with Scikit-Learn",
                "Build end-to-end machine learning inference pipelines"
            ],
            "requirements": [
                "Basic understanding of Python variables, functions, and control flow"
            ],
            "instructor": {
                "name": "Dr. Sophia Chen",
                "title": "Senior Data Scientist & AI Researcher",
                "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&q=80",
                "bio": "PhD in Computer Science. Former Machine Learning Engineer at top Silicon Valley labs."
            },
            "lessons": [
                {
                    "id": "lesson-201",
                    "title": "Data Science Workflow and Environment Setup",
                    "description": "Jupyter notebooks, virtual environments, and working with analytical libraries.",
                    "duration": "18:30",
                    "video_url": SAMPLE_VIDEOS[0],
                    "order": 1,
                    "is_preview": True
                },
                {
                    "id": "lesson-202",
                    "title": "Numerical Computing with NumPy Arrays",
                    "description": "Broadcasting, vectorization, array manipulation, and memory-efficient matrix operations.",
                    "duration": "24:10",
                    "video_url": SAMPLE_VIDEOS[1],
                    "order": 2,
                    "is_preview": False
                },
                {
                    "id": "lesson-203",
                    "title": "Data Wrangling & Exploratory Analysis with Pandas",
                    "description": "Filtering, aggregation, pivot tables, handling missing values, and time series analysis.",
                    "duration": "34:50",
                    "video_url": SAMPLE_VIDEOS[2],
                    "order": 3,
                    "is_preview": False
                },
                {
                    "id": "lesson-204",
                    "title": "Supervised Learning: Regression and Classification",
                    "description": "Linear regression, decision trees, random forests, and cross-validation techniques.",
                    "duration": "30:15",
                    "video_url": SAMPLE_VIDEOS[3],
                    "order": 4,
                    "is_preview": False
                },
                {
                    "id": "lesson-205",
                    "title": "Model Evaluation, Tuning & Deployment",
                    "description": "ROC-AUC metrics, confusion matrices, hyperparameter grid search, and model export.",
                    "duration": "27:40",
                    "video_url": SAMPLE_VIDEOS[4],
                    "order": 5,
                    "is_preview": False
                }
            ]
        },
        {
            "title": "UI/UX Design Masterclass: Figma to Interactive Prototypes",
            "slug": "ui-ux-design-masterclass-figma",
            "category": "UI/UX Design",
            "difficulty": "All Levels",
            "duration": "14h 45m",
            "price": 39.99,
            "featured": True,
            "rating": 4.9,
            "reviews_count": 1890,
            "students_enrolled": 8410,
            "thumbnail": "https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?w=800&q=80",
            "short_description": "Craft stunning digital user experiences, typography systems, color theory, and micro-interactions in Figma.",
            "description": "Learn the principles of human-computer interaction, visual hierarchy, user research, wireframing, design systems, and animated interactive prototyping.",
            "learning_objectives": [
                "Master Figma components, auto-layout, variants, and design tokens",
                "Apply visual hierarchy, typographic scales, and harmonious color palettes",
                "Conduct user journey mapping and usability heuristics evaluations",
                "Build click-through interactive prototypes ready for user testing"
            ],
            "requirements": [
                "No prior design software experience required; Figma account is free"
            ],
            "instructor": {
                "name": "Marcus Vance",
                "title": "Head of Product Design",
                "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80",
                "bio": "Award-winning product designer behind top consumer applications and design systems."
            },
            "lessons": [
                {
                    "id": "lesson-301",
                    "title": "Design Thinking & UX Foundations",
                    "description": "User personas, problem framing, information architecture, and user flow mapping.",
                    "duration": "16:45",
                    "video_url": SAMPLE_VIDEOS[0],
                    "order": 1,
                    "is_preview": True
                },
                {
                    "id": "lesson-302",
                    "title": "Figma Auto-Layout & Design Systems",
                    "description": "Mastering responsive layout constraints, nested frames, and reusable component libraries.",
                    "duration": "26:10",
                    "video_url": SAMPLE_VIDEOS[1],
                    "order": 2,
                    "is_preview": False
                },
                {
                    "id": "lesson-303",
                    "title": "Color Theory, Contrast Accessibility & Typography",
                    "description": "WCAG compliance, optical balance, type scale pairing, and dark mode tokens.",
                    "duration": "21:30",
                    "video_url": SAMPLE_VIDEOS[2],
                    "order": 3,
                    "is_preview": False
                },
                {
                    "id": "lesson-304",
                    "title": "Interactive Prototyping & Smart Animate",
                    "description": "Micro-interactions, state transitions, animated modal dialogues, and gestures.",
                    "duration": "29:15",
                    "video_url": SAMPLE_VIDEOS[3],
                    "order": 4,
                    "is_preview": False
                }
            ]
        },
        {
            "title": "Cloud Architecture & DevOps with Docker & Kubernetes",
            "slug": "cloud-architecture-devops-docker-kubernetes",
            "category": "Cloud & DevOps",
            "difficulty": "Advanced",
            "duration": "16h 20m",
            "price": 69.99,
            "featured": False,
            "rating": 4.7,
            "reviews_count": 940,
            "students_enrolled": 4200,
            "thumbnail": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80",
            "short_description": "Build resilient CI/CD pipelines, containerize applications, and orchestrate microservices with Kubernetes.",
            "description": "A deep dive into cloud-native engineering. Learn containerization fundamentals with Docker, cluster orchestration with Kubernetes, Helm charts, automated GitHub Actions pipelines, and zero-downtime deployments.",
            "learning_objectives": [
                "Write optimized multi-stage Dockerfiles for web applications",
                "Deploy and manage Kubernetes pods, deployments, services, and ingresses",
                "Set up automated CI/CD build, test, and release workflows",
                "Implement centralized logging, Prometheus monitoring, and health probes"
            ],
            "requirements": [
                "Familiarity with Linux terminal commands and basic web development"
            ],
            "instructor": {
                "name": "Elena Rostova",
                "title": "Cloud Infrastructure Architect",
                "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&q=80",
                "bio": "Certified Kubernetes Administrator (CKA) and Cloud Security Specialist."
            },
            "lessons": [
                {
                    "id": "lesson-401",
                    "title": "Docker Containers & Multi-Stage Builds",
                    "description": "Container architecture, Docker CLI, layer caching, and minimizing image footprints.",
                    "duration": "20:10",
                    "video_url": SAMPLE_VIDEOS[0],
                    "order": 1,
                    "is_preview": True
                },
                {
                    "id": "lesson-402",
                    "title": "Kubernetes Cluster Architecture & Core Concepts",
                    "description": "Control plane components, nodes, pods, replica sets, and declarative YAML specs.",
                    "duration": "32:00",
                    "video_url": SAMPLE_VIDEOS[1],
                    "order": 2,
                    "is_preview": False
                },
                {
                    "id": "lesson-403",
                    "title": "Networking, Ingress & Secret Management",
                    "description": "ClusterIP, NodePort, LoadBalancer, TLS certificates, and encrypted secrets.",
                    "duration": "25:40",
                    "video_url": SAMPLE_VIDEOS[2],
                    "order": 3,
                    "is_preview": False
                },
                {
                    "id": "lesson-404",
                    "title": "CI/CD Automation & Production Deployments",
                    "description": "Automated pipelines, rolling updates, canary rollouts, and rollback triggers.",
                    "duration": "28:15",
                    "video_url": SAMPLE_VIDEOS[3],
                    "order": 4,
                    "is_preview": False
                }
            ]
        },
        {
            "title": "Cybersecurity Fundamentals: Defense & Ethical Hacking",
            "slug": "cybersecurity-fundamentals-defense-ethical-hacking",
            "category": "Cybersecurity",
            "difficulty": "Intermediate",
            "duration": "15h 00m",
            "price": 54.99,
            "featured": False,
            "rating": 4.8,
            "reviews_count": 1120,
            "students_enrolled": 5600,
            "thumbnail": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&q=80",
            "short_description": "Understand network security, penetration testing methodologies, OWASP Top 10 vulnerabilities, and defense.",
            "description": "Gain hands-on understanding of cybersecurity threat models, defensive counter-measures, penetration testing ethics, SQL injection, XSS prevention, and cryptography.",
            "learning_objectives": [
                "Identify and remediate OWASP Top 10 web application vulnerabilities",
                "Analyze network traffic packets with Wireshark",
                "Implement secure authentication, token storage, and encryption algorithms",
                "Establish defensive posture and incident response procedures"
            ],
            "requirements": [
                "Basic understanding of IP networking and operating systems"
            ],
            "instructor": {
                "name": "James Macintyre",
                "title": "Chief Information Security Officer",
                "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&q=80",
                "bio": "Certified Ethical Hacker (CEH) with 12+ years defending enterprise infrastructures."
            },
            "lessons": [
                {
                    "id": "lesson-501",
                    "title": "Threat Modeling and the Ethical Hacker Mindset",
                    "description": "Security triad (CIA), attack vectors, reconnaissance, and ethical boundaries.",
                    "duration": "18:40",
                    "video_url": SAMPLE_VIDEOS[0],
                    "order": 1,
                    "is_preview": True
                },
                {
                    "id": "lesson-502",
                    "title": "Network Scanning & Port Enumeration",
                    "description": "Nmap scanning techniques, service banner grabbing, and firewall bypass concepts.",
                    "duration": "24:30",
                    "video_url": SAMPLE_VIDEOS[1],
                    "order": 2,
                    "is_preview": False
                },
                {
                    "id": "lesson-503",
                    "title": "Web Application Attacks: SQLi, XSS & CSRF",
                    "description": "Exploitation mechanics, payload crafting, and bulletproof input sanitization defenses.",
                    "duration": "35:10",
                    "video_url": SAMPLE_VIDEOS[2],
                    "order": 3,
                    "is_preview": False
                },
                {
                    "id": "lesson-504",
                    "title": "Cryptography, SSL/TLS & Key Management",
                    "description": "Symmetric and asymmetric encryption, digital signatures, hashing vs encryption.",
                    "duration": "22:50",
                    "video_url": SAMPLE_VIDEOS[3],
                    "order": 4,
                    "is_preview": False
                }
            ]
        },
        {
            "title": "Cross-Platform Mobile App Development with Flutter & Dart",
            "slug": "mobile-app-development-flutter-dart",
            "category": "Mobile Development",
            "difficulty": "Beginner",
            "duration": "17h 10m",
            "price": 44.99,
            "featured": False,
            "rating": 4.8,
            "reviews_count": 1450,
            "students_enrolled": 6700,
            "thumbnail": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=800&q=80",
            "short_description": "Build high-performance, native iOS and Android apps with a single modern codebase using Flutter.",
            "description": "Learn Flutter widget architecture, reactive state management with Riverpod, animations, REST API data fetching, and native device hardware integrations.",
            "learning_objectives": [
                "Master Dart syntax, asynchronous streams, and object-oriented programming",
                "Compose beautiful native-feeling UI screens with Flutter widgets",
                "Manage complex application state cleanly and testably",
                "Publish mobile applications to the Apple App Store and Google Play Store"
            ],
            "requirements": [
                "Any operating system with basic programming fundamentals"
            ],
            "instructor": {
                "name": "Maya Patel",
                "title": "Mobile Engineering Lead",
                "avatar": "https://images.unsplash.com/photo-1548142813-c348350df52b?w=400&q=80",
                "bio": "Lead mobile developer with over 20 published apps and 5M+ installs worldwide."
            },
            "lessons": [
                {
                    "id": "lesson-601",
                    "title": "Flutter Ecosystem & Dart Essentials",
                    "description": "Dart types, functions, async/await, and setting up the Flutter SDK emulator.",
                    "duration": "19:25",
                    "video_url": SAMPLE_VIDEOS[0],
                    "order": 1,
                    "is_preview": True
                },
                {
                    "id": "lesson-602",
                    "title": "Widget Tree & Stateless vs Stateful Widgets",
                    "description": "Understanding composition, build contexts, scaffolding, and responsive layouts.",
                    "duration": "27:10",
                    "video_url": SAMPLE_VIDEOS[1],
                    "order": 2,
                    "is_preview": False
                },
                {
                    "id": "lesson-603",
                    "title": "Reactive State Management with Providers",
                    "description": "Separation of concerns, reactive data binding, and maintaining clean architecture.",
                    "duration": "30:45",
                    "video_url": SAMPLE_VIDEOS[2],
                    "order": 3,
                    "is_preview": False
                },
                {
                    "id": "lesson-604",
                    "title": "Networking, HTTP Requests & Offline Storage",
                    "description": "Consuming REST APIs, serializing JSON models, and caching with local storage.",
                    "duration": "25:30",
                    "video_url": SAMPLE_VIDEOS[3],
                    "order": 4,
                    "is_preview": False
                }
            ]
        }
    ]

    created_courses = []
    for c_data in courses_data:
        c, err = CourseModel.create_course(c_data)
        if c and not quiet:
            created_courses.append(c)
            print(f"  Added course: {c['title']} ({len(c['lessons'])} lessons)")
        elif c:
            created_courses.append(c)

    if not quiet:
        print("[LearnHub Seed] Pre-enrolling demo student into courses with progress...")
    student_id = student_user["id"]
    course_1 = created_courses[0]
    course_2 = created_courses[1]

    # Enroll in course 1 and mark first 2 lessons completed
    EnrollmentModel.enroll_user(student_id, course_1["id"])
    ProgressModel.mark_lesson_completed(student_id, course_1["id"], course_1["lessons"][0]["id"])
    ProgressModel.mark_lesson_completed(student_id, course_1["id"], course_1["lessons"][1]["id"])

    # Enroll in course 2 (not started yet)
    EnrollmentModel.enroll_user(student_id, course_2["id"])

    # Enroll secondary student in course 1
    EnrollmentModel.enroll_user(student_user_2["id"], course_1["id"])

    if not quiet:
        print("\n[LearnHub Seed] Seed completed successfully!")
    print("----------------------------------------------------------------")
    print(" Credentials for testing:")
    print(" 1) Admin Account:")
    print("    Email:    admin@learnhub.com")
    print("    Password: Admin@12345")
    print(" 2) Student Account:")
    print("    Email:    student@learnhub.com")
    print("    Password: Student@12345")
    print(" 3) Second Student:")
    print("    Email:    emma@learnhub.com")
    print("    Password: Student@12345")
    print("----------------------------------------------------------------")

if __name__ == "__main__":
    init_db()
    seed_database()
