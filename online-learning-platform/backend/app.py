import os
import sys
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

# Add root folder to sys.path so 'backend' package imports work cleanly
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.config import Config, init_db, is_real_mongo
from backend.routes.auth_routes import auth_bp
from backend.routes.course_routes import course_bp
from backend.routes.enrollment_routes import enrollment_bp
from backend.routes.progress_routes import progress_bp
from backend.routes.admin_routes import admin_bp

def create_app(test_config=None):
    frontend_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
    app = Flask(__name__, static_folder=frontend_folder, static_url_path="")

    # Configuration
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["SESSION_COOKIE_HTTPONLY"] = Config.SESSION_COOKIE_HTTPONLY
    app.config["SESSION_COOKIE_SAMESITE"] = Config.SESSION_COOKIE_SAMESITE
    app.config["SESSION_COOKIE_SECURE"] = Config.SESSION_COOKIE_SECURE

    if test_config:
        app.config.update(test_config)

    # Initialize CORS
    CORS(
        app,
        supports_credentials=True,
        origins=Config.CORS_ORIGINS,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"]
    )

    # Initialize Database
    force_mock = test_config.get("FORCE_MOCK_DB", False) if test_config else False
    db = init_db(app, force_mock=force_mock)

    # Automatically seed sample data if courses collection is empty
    try:
        from backend.seed import seed_database
        if db["courses"].count_documents({}) == 0:
            seed_database(quiet=True)
    except Exception as e:
        print(f"[LearnHub] Auto-seed note: {e}")

    # Register API Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(enrollment_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(admin_bp)

    # Health check route
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "LearnHub Backend API",
            "database": "mongodb" if is_real_mongo() else "mongomock (development/testing mode)",
            "version": "1.0.0"
        }), 200

    # Frontend Static File Serving
    @app.route("/", methods=["GET"])
    def index():
        return send_from_directory(frontend_folder, "index.html")

    @app.route("/<path:path>", methods=["GET"])
    def static_proxy(path):
        # If path exists in frontend folder, serve it
        full_path = os.path.join(frontend_folder, path)
        if os.path.isfile(full_path):
            return send_from_directory(frontend_folder, path)
        # If it's a known page without .html, append .html
        html_candidate = full_path + ".html"
        if os.path.isfile(html_candidate):
            return send_from_directory(frontend_folder, path + ".html")
        return send_from_directory(frontend_folder, "index.html")

    # Centralized Error Handlers
    @app.errorhandler(400)
    def bad_request(e):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": "Bad Request", "message": str(e)}), 400
        return "Bad Request", 400

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": "Not Found", "message": "The requested API endpoint was not found"}), 404
        return send_from_directory(frontend_folder, "index.html")

    @app.errorhandler(500)
    def internal_error(e):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": "Internal Server Error", "message": "An unexpected error occurred"}), 500
        return "Internal Server Error", 500

    return app


if __name__ == "__main__":
    app = create_app()
    port = Config.PORT
    print(f"\n========================================================")
    print(f" LearnHub Online Learning Platform Server")
    print(f" URL: http://localhost:{port}")
    print(f" API Base: http://localhost:{port}/api")
    print(f" Database Mode: {'Live MongoDB' if is_real_mongo() else 'mongomock (In-Memory)'}")
    print(f"========================================================\n")
    app.run(host="0.0.0.0", port=port, debug=Config.DEBUG)
