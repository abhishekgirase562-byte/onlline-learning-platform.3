from flask import Blueprint, jsonify
from backend.services.enrollment_service import EnrollmentService
from backend.middleware.auth_middleware import login_required, get_current_user_id

enrollment_bp = Blueprint("enrollment_bp", __name__, url_prefix="/api/enrollments")

@enrollment_bp.route("/<course_id>", methods=["POST"])
@login_required
def enroll(course_id):
    user_id = get_current_user_id()
    enrollment, err = EnrollmentService.enroll(user_id, course_id)

    if err and "Already enrolled" in err:
        return jsonify({
            "success": True,
            "message": "You are already enrolled in this course.",
            "enrollment": enrollment
        }), 200

    if err:
        return jsonify({"success": False, "message": err}), 400

    return jsonify({
        "success": True,
        "message": "Successfully enrolled in course!",
        "enrollment": enrollment
    }), 201


@enrollment_bp.route("/my-courses", methods=["GET"])
@login_required
def get_my_courses():
    user_id = get_current_user_id()
    dashboard_data = EnrollmentService.get_user_dashboard(user_id)
    return jsonify({
        "success": True,
        "data": dashboard_data
    }), 200


@enrollment_bp.route("/<course_id>/status", methods=["GET"])
def check_status(course_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": True, "is_enrolled": False}), 200

    is_enrolled = EnrollmentService.is_enrolled(user_id, course_id)
    return jsonify({
        "success": True,
        "is_enrolled": is_enrolled
    }), 200
