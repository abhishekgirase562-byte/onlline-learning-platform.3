def test_student_forbidden_from_admin(client):
    # Log in as student
    client.post("/api/auth/login", json={
        "email": "student@learnhub.com",
        "password": "Student@12345"
    })

    # Try to access admin stats
    res = client.get("/api/admin/stats")
    assert res.status_code == 403
    assert res.get_json()["success"] is False


def test_admin_stats_and_students(client):
    # Log in as admin
    client.post("/api/auth/login", json={
        "email": "admin@learnhub.com",
        "password": "Admin@12345"
    })

    # Fetch stats
    stats_res = client.get("/api/admin/stats")
    assert stats_res.status_code == 200
    stats = stats_res.get_json()["stats"]
    assert stats["total_courses"] >= 6
    assert stats["total_students"] >= 2

    # Fetch students
    students_res = client.get("/api/admin/students")
    assert students_res.status_code == 200
    students = students_res.get_json()["students"]
    assert len(students) >= 2


def test_admin_course_crud(client):
    # Log in as admin
    client.post("/api/auth/login", json={
        "email": "admin@learnhub.com",
        "password": "Admin@12345"
    })

    # Create new course
    create_res = client.post("/api/courses", json={
        "title": "Quantum Computing 101",
        "category": "Quantum",
        "difficulty": "Advanced",
        "price": 89.99,
        "description": "Introduction to qubits and quantum algorithms.",
        "lessons": [
            {
                "title": "Qubits and Superposition",
                "duration": "15:00",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
            }
        ]
    })
    assert create_res.status_code == 201
    course_id = create_res.get_json()["course"]["id"]

    # Add a lesson
    lesson_res = client.post(f"/api/courses/{course_id}/lessons", json={
        "title": "Quantum Entanglement",
        "duration": "20:00",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4"
    })
    assert lesson_res.status_code == 201

    # Delete the course
    del_res = client.delete(f"/api/courses/{course_id}")
    assert del_res.status_code == 200
