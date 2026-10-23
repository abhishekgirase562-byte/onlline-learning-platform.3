import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("learnhub")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "learnhub-super-secret-key-change-in-production-2026")
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/learnhub")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "learnhub")
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5000,http://127.0.0.1:5000,http://localhost:3000,http://127.0.0.1:5500"
        ).split(",")
        if origin.strip()
    ]
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False  # Set to True in production over HTTPS


_db_client = None
_db_instance = None
_db_is_real_mongo = False


def init_db(app=None, force_mock=False):
    """
    Initializes and returns the MongoDB database.
    Attempts to connect to real MongoDB using pymongo.
    If unavailable or force_mock is True, falls back to mongomock for safe local development/testing.
    """
    global _db_client, _db_instance, _db_is_real_mongo
    if _db_instance is not None and not force_mock:
        return _db_instance

    mongo_uri = Config.MONGO_URI
    db_name = Config.MONGO_DB_NAME

    if not force_mock:
        try:
            import pymongo
            client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=1500)
            # Ping the database to verify live connectivity
            client.admin.command("ping")
            _db_client = client
            _db_instance = client[db_name]
            _db_is_real_mongo = True
            logger.info(f"[LearnHub DB] Successfully connected to live MongoDB at: {mongo_uri}")
            return _db_instance
        except Exception as e:
            logger.warning(
                f"[LearnHub DB] Live MongoDB not accessible at {mongo_uri} ({e}). "
                "Falling back to in-memory mongomock database. All operations will succeed."
            )

    try:
        import mongomock
        _db_client = mongomock.MongoClient()
        _db_instance = _db_client[db_name]
        _db_is_real_mongo = False
        logger.info(f"[LearnHub DB] Initialized in-memory MongoDB (mongomock) for database '{db_name}'.")
        return _db_instance
    except Exception as e:
        logger.error(f"Failed to initialize mongomock database: {e}")
        raise


def get_db():
    global _db_instance
    if _db_instance is None:
        init_db()
    return _db_instance


def is_real_mongo():
    global _db_is_real_mongo
    return _db_is_real_mongo
