from functools import wraps
from flask import session, jsonify, request
from backend.models.user_model import UserModel

def get_current_user_id():
    return session.get("user_id")

def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    user = UserModel.find_by_id(user_id)
    return UserModel.sanitize(user) if user else None


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({
                "success": False,
                "message": "Authentication required. Please log in to proceed."
            }), 401
        
        # Verify user still exists in database
        user = UserModel.find_by_id(user_id)
        if not user:
            session.clear()
            return jsonify({
                "success": False,
                "message": "Session expired or user not found. Please log in again."
            }), 401

        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({
                "success": False,
                "message": "Authentication required. Please log in as an administrator."
            }), 401

        user = UserModel.find_by_id(user_id)
        if not user or user.get("role") != "admin":
            return jsonify({
                "success": False,
                "message": "Access denied. Administrator privileges required."
            }), 403

        return f(*args, **kwargs)
    return decorated_function
