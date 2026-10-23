from flask import Blueprint, request, jsonify
from backend.services.auth_service import AuthService
from backend.middleware.auth_middleware import login_required, get_current_user_id
from backend.models.user_model import UserModel

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "student")
    bio = data.get("bio", "")

    user, err = AuthService.register(name, email, password, role=role, bio=bio)
    if err:
        return jsonify({"success": False, "message": err}), 400

    return jsonify({
        "success": True,
        "message": "Account created successfully",
        "user": user
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    user, err = AuthService.login(email, password)
    if err:
        return jsonify({"success": False, "message": err}), 401

    return jsonify({
        "success": True,
        "message": f"Welcome back, {user['name']}!",
        "user": user
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    AuthService.logout()
    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    }), 200


@auth_bp.route("/me", methods=["GET"])
def get_me():
    user = AuthService.get_current_user_profile()
    if not user:
        return jsonify({
            "success": False,
            "authenticated": False,
            "user": None
        }), 200

    return jsonify({
        "success": True,
        "authenticated": True,
        "user": user
    }), 200


@auth_bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    user_id = get_current_user_id()
    data = request.get_json() or {}
    name = data.get("name")
    bio = data.get("bio")
    avatar = data.get("avatar")

    updated, err = UserModel.update_profile(user_id, name=name, bio=bio, avatar=avatar)
    if err:
        return jsonify({"success": False, "message": err}), 400

    return jsonify({
        "success": True,
        "message": "Profile updated successfully",
        "user": updated
    }), 200
