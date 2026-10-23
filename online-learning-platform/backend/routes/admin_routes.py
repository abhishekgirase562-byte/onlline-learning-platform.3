from flask import Blueprint, jsonify
from backend.services.admin_service import AdminService
from backend.middleware.auth_middleware import admin_required
from backend.models.user_model import UserModel

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/api/admin")

@admin_bp.route("/stats", methods=["GET"])
@admin_required
def get_stats():
    stats = AdminService.get_stats()
    return jsonify({
        "success": True,
        "stats": stats
    }), 200


@admin_bp.route("/students", methods=["GET"])
@admin_required
def get_students():
    students = AdminService.get_students()
    return jsonify({
        "success": True,
        "students": students
    }), 200


@admin_bp.route("/enrollments", methods=["GET"])
@admin_required
def get_enrollments():
    enrollments = AdminService.get_enrollments()
    return jsonify({
        "success": True,
        "enrollments": enrollments
    }), 200


@admin_bp.route("/users/<user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    success = UserModel.delete_user(user_id)
    if not success:
        return jsonify({"success": False, "message": "User not found or could not be deleted"}), 404

    return jsonify({
        "success": True,
        "message": "User deleted successfully"
    }), 200
