from datetime import datetime, timezone
from backend.config import get_db
from backend.models.utils import serialize_doc, to_object_id
from backend.models.course_model import CourseModel

def get_enrollments_collection():
    return get_db()["enrollments"]

class EnrollmentModel:
    @staticmethod
    def enroll_user(user_id, course_id):
        collection = get_enrollments_collection()
        uid = str(user_id)
        cid = str(course_id)

        # Check existing enrollment
        existing = collection.find_one({"user_id": uid, "course_id": cid})
        if existing:
            return serialize_doc(existing), "Already enrolled in this course"

        # Verify course exists
        course = CourseModel.find_by_id(cid)
        if not course:
            return None, "Course does not exist"

        now = datetime.now(timezone.utc)
        enrollment_doc = {
            "user_id": uid,
            "course_id": cid,
            "status": "active",
            "enrolled_at": now,
            "completed_at": None
        }

        res = collection.insert_one(enrollment_doc)
        enrollment_doc["_id"] = res.inserted_id

        # Increment students_enrolled counter on course
        CourseModel.increment_enrollment(cid, 1)

        # Initialize progress record
        from backend.models.progress_model import ProgressModel
        ProgressModel.get_or_create_progress(uid, cid)

        return serialize_doc(enrollment_doc), None

    @staticmethod
    def is_enrolled(user_id, course_id):
        if not user_id or not course_id:
            return False
        collection = get_enrollments_collection()
        doc = collection.find_one({
            "user_id": str(user_id),
            "course_id": str(course_id),
            "status": "active"
        })
        return doc is not None

    @staticmethod
    def get_user_enrollments(user_id):
        collection = get_enrollments_collection()
        docs = list(collection.find({"user_id": str(user_id)}).sort("enrolled_at", -1))
        return [serialize_doc(d) for d in docs]

    @staticmethod
    def get_all_enrollments():
        collection = get_enrollments_collection()
        docs = list(collection.find().sort("enrolled_at", -1))
        return [serialize_doc(d) for d in docs]

    @staticmethod
    def count_enrollments():
        collection = get_enrollments_collection()
        return collection.count_documents({})
