import re
from flask import session
from backend.models.user_model import UserModel

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

class AuthService:
    @staticmethod
    def register(name, email, password, role="student", bio=""):
        if not name or len(name.strip()) < 2:
            return None, "Full name must be at least 2 characters long"
        
        if not email or not re.match(EMAIL_REGEX, email.strip()):
            return None, "Please enter a valid email address"
            
        if not password or len(password) < 6:
            return None, "Password must be at least 6 characters long"

        # Validate allowed roles
        valid_role = "admin" if role == "admin" else "student"

        user, err = UserModel.create_user(
            name=name.strip(),
            email=email.strip(),
            password=password,
            role=valid_role,
            bio=bio
        )

        if err:
            return None, err

        # Set session on registration
        session["user_id"] = user["id"]
        session["role"] = user["role"]
        session["name"] = user["name"]
        session["email"] = user["email"]

        return user, None

    @staticmethod
    def login(email, password):
        if not email or not password:
            return None, "Email and password are required"

        user = UserModel.find_by_email(email)
        if not user:
            return None, "Invalid email or password"

        if not UserModel.verify_password(user.get("password_hash"), password):
            return None, "Invalid email or password"

        sanitized = UserModel.sanitize(user)
        session["user_id"] = sanitized["id"]
        session["role"] = sanitized["role"]
        session["name"] = sanitized["name"]
        session["email"] = sanitized["email"]

        return sanitized, None

    @staticmethod
    def logout():
        session.clear()
        return True

    @staticmethod
    def get_current_user_profile():
        user_id = session.get("user_id")
        if not user_id:
            return None
        user = UserModel.find_by_id(user_id)
        return UserModel.sanitize(user) if user else None
