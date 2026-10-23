from flask import Blueprint, jsonify
from backend.services.progress_service import ProgressService
from backend.middleware.auth_middleware import login_required, get_current_user_id

progress_bp = Blueprint("progress_bp", __name__, url_prefix="/api/progress")

@progress_bp.route("/<course_id>", methods=["GET"])
@login_required
def get_progress(course_id):
    user_id = get_current_user_id()
    prog = ProgressService.get_progress(user_id, course_id)
    return jsonify({
        "success": True,
        "progress": prog
    }), 200


@progress_bp.route("/<course_id>/lessons/<lesson_id>/complete", methods=["POST"])
@login_required
def complete_lesson(course_id, lesson_id):
    user_id = get_current_user_id()
    prog = ProgressService.complete_lesson(user_id, course_id, lesson_id)
    return jsonify({
        "success": True,
        "message": "Lesson marked as completed!",
        "progress": prog
    }), 200


@progress_bp.route("/<course_id>/lessons/<lesson_id>/uncomplete", methods=["POST"])
@login_required
def uncomplete_lesson(course_id, lesson_id):
    user_id = get_current_user_id()
    prog = ProgressService.uncomplete_lesson(user_id, course_id, lesson_id)
    return jsonify({
        "success": True,
        "message": "Lesson marked as incomplete.",
        "progress": prog
    }), 200
