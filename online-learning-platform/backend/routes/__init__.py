from backend.routes.auth_routes import auth_bp
from backend.routes.course_routes import course_bp
from backend.routes.enrollment_routes import enrollment_bp
from backend.routes.progress_routes import progress_bp
from backend.routes.admin_routes import admin_bp

__all__ = ["auth_bp", "course_bp", "enrollment_bp", "progress_bp", "admin_bp"]
