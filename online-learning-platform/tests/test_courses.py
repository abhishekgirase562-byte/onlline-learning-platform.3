def test_get_all_courses(client):
    res = client.get("/api/courses")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["count"] >= 6


def test_filter_courses_by_category(client):
    res = client.get("/api/courses?category=Web%20Development")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    for c in data["courses"]:
        assert c["category"].lower() == "web development"


def test_search_courses(client):
    res = client.get("/api/courses?search=Python")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert any("python" in c["title"].lower() for c in data["courses"])


def test_get_course_details_and_lesson_protection(client):
    # Get course list first
    courses_res = client.get("/api/courses")
    first_course = courses_res.get_json()["courses"][0]
    course_id = first_course["id"]

    # Request as unauthenticated visitor
    res = client.get(f"/api/courses/{course_id}")
    assert res.status_code == 200
    course_data = res.get_json()["course"]
    assert course_data["id"] == course_id

    # Verify that non-preview lessons have video_url stripped / locked
    for lesson in course_data["lessons"]:
        if not lesson.get("is_preview"):
            assert lesson["video_url"] is None
            assert lesson["is_locked"] is True
        else:
            assert lesson["is_locked"] is False
