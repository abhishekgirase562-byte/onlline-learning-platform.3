from flask import Blueprint, request, jsonify, session
from backend.services.course_service import CourseService
from backend.middleware.auth_middleware import admin_required, get_current_user_id

course_bp = Blueprint("course_bp", __name__, url_prefix="/api/courses")

@course_bp.route("", methods=["GET"])
def get_courses():
    search = request.args.get("search", "").strip() or None
    category = request.args.get("category", "").strip() or None
    difficulty = request.args.get("difficulty", "").strip() or None
    sort_by = request.args.get("sort_by", "").strip() or None
    featured = request.args.get("featured", "").lower() in ("true", "1")

    limit_param = request.args.get("limit")
    limit = int(limit_param) if limit_param and limit_param.isdigit() else None

    courses = CourseService.list_courses(
        search=search,
        category=category,
        difficulty=difficulty,
        featured_only=featured,
        sort_by=sort_by,
        limit=limit
    )

    return jsonify({
        "success": True,
        "count": len(courses),
        "courses": courses
    }), 200


@course_bp.route("/<course_id>", methods=["GET"])
def get_course_details(course_id):
    current_user_id = get_current_user_id()
    is_admin = session.get("role") == "admin"

    course, err = CourseService.get_course_details(
        course_id=course_id,
        current_user_id=current_user_id,
        is_admin=is_admin
    )

    if err or not course:
        return jsonify({"success": False, "message": err or "Course not found"}), 404

    return jsonify({
        "success": True,
        "course": course
    }), 200


@course_bp.route("", methods=["POST"])
@admin_required
def create_course():
    data = request.get_json() or {}
    if not data.get("title"):
        return jsonify({"success": False, "message": "Course title is required"}), 400

    course, err = CourseService.create_course(data)
    if err:
        return jsonify({"success": False, "message": err}), 400

    return jsonify({
        "success": True,
        "message": "Course created successfully",
        "course": course
    }), 201


@course_bp.route("/<course_id>", methods=["PUT"])
@admin_required
def update_course(course_id):
    data = request.get_json() or {}
    course, err = CourseService.update_course(course_id, data)
    if err:
        return jsonify({"success": False, "message": err}), 400

    return jsonify({
        "success": True,
        "message": "Course updated successfully",
        "course": course
    }), 200


@course_bp.route("/<course_id>", methods=["DELETE"])
@admin_required
def delete_course(course_id):
    success = CourseService.delete_course(course_id)
    if not success:
        return jsonify({"success": False, "message": "Failed to delete course or not found"}), 404

    return jsonify({
        "success": True,
        "message": "Course deleted successfully"
    }), 200


@course_bp.route("/<course_id>/lessons", methods=["POST"])
@admin_required
def add_lesson(course_id):
    data = request.get_json() or {}
    if not data.get("title"):
        return jsonify({"success": False, "message": "Lesson title is required"}), 400

    lesson, err = CourseService.add_lesson(course_id, data)
    if err:
        return jsonify({"success": False, "message": err}), 400

    return jsonify({
        "success": True,
        "message": "Lesson added successfully",
        "lesson": lesson
    }), 201


@course_bp.route("/<course_id>/lessons/<lesson_id>", methods=["PUT"])
@admin_required
def update_lesson(course_id, lesson_id):
    data = request.get_json() or {}
    lesson, err = CourseService.update_lesson(course_id, lesson_id, data)
    if err:
        return jsonify({"success": False, "message": err}), 400

    return jsonify({
        "success": True,
        "message": "Lesson updated successfully",
        "lesson": lesson
    }), 200


@course_bp.route("/<course_id>/lessons/<lesson_id>", methods=["DELETE"])
@admin_required
def delete_lesson(course_id, lesson_id):
    res, err = CourseService.delete_lesson(course_id, lesson_id)
    if err:
        return jsonify({"success": False, "message": err}), 400

    return jsonify({
        "success": True,
        "message": "Lesson deleted successfully"
    }), 200
