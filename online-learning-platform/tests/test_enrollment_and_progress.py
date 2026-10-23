def test_enrollment_and_progress(client):
    # Log in as demo student
    login_res = client.post("/api/auth/login", json={
        "email": "student@learnhub.com",
        "password": "Student@12345"
    })
    assert login_res.status_code == 200

    # Get a course that the student is not yet enrolled in (e.g. course index 2 or 3)
    courses_res = client.get("/api/courses")
    courses = courses_res.get_json()["courses"]
    course_to_enroll = courses[2]
    course_id = course_to_enroll["id"]

    # Enroll in course
    enroll_res = client.post(f"/api/enrollments/{course_id}")
    assert enroll_res.status_code in (200, 201)
    assert enroll_res.get_json()["success"] is True

    # Check status
    status_res = client.get(f"/api/enrollments/{course_id}/status")
    assert status_res.status_code == 200
    assert status_res.get_json()["is_enrolled"] is True

    # Mark first lesson complete
    lesson_id = course_to_enroll["lessons"][0]["id"]
    complete_res = client.post(f"/api/progress/{course_id}/lessons/{lesson_id}/complete")
    assert complete_res.status_code == 200
    progress_data = complete_res.get_json()["progress"]
    assert lesson_id in progress_data["completed_lessons"]
    assert progress_data["progress_percentage"] > 0

    # Fetch dashboard
    dashboard_res = client.get("/api/enrollments/my-courses")
    assert dashboard_res.status_code == 200
    dash_data = dashboard_res.get_json()["data"]
    assert dash_data["stats"]["total_enrolled"] >= 2
    assert any(c["course_id"] == course_id for c in dash_data["enrolled_courses"])
