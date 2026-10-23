from datetime import datetime, timezone
from backend.config import get_db
from backend.models.utils import serialize_doc
from backend.models.course_model import CourseModel

def get_progress_collection():
    return get_db()["lesson_progress"]


class ProgressModel:
    @staticmethod
    def get_or_create_progress(user_id, course_id):
        collection = get_progress_collection()
        uid = str(user_id)
        cid = str(course_id)

        doc = collection.find_one({"user_id": uid, "course_id": cid})
        if doc:
            return serialize_doc(doc)

        now = datetime.now(timezone.utc)
        new_doc = {
            "user_id": uid,
            "course_id": cid,
            "completed_lessons": [],
            "last_lesson_id": None,
            "progress_percentage": 0.0,
            "is_completed": False,
            "updated_at": now
        }

        res = collection.insert_one(new_doc)
        new_doc["_id"] = res.inserted_id
        return serialize_doc(new_doc)

    @staticmethod
    def get_progress(user_id, course_id):
        collection = get_progress_collection()
        doc = collection.find_one({"user_id": str(user_id), "course_id": str(course_id)})
        if not doc:
            return {
                "user_id": str(user_id),
                "course_id": str(course_id),
                "completed_lessons": [],
                "last_lesson_id": None,
                "progress_percentage": 0.0,
                "is_completed": False
            }
        return serialize_doc(doc)

    @staticmethod
    def mark_lesson_completed(user_id, course_id, lesson_id):
        collection = get_progress_collection()
        uid = str(user_id)
        cid = str(course_id)
        lid = str(lesson_id)

        course = CourseModel.find_by_id(cid)
        total_lessons = len(course.get("lessons", [])) if course else 1
        if total_lessons == 0:
            total_lessons = 1

        doc = collection.find_one({"user_id": uid, "course_id": cid})
        if not doc:
            ProgressModel.get_or_create_progress(uid, cid)
            doc = collection.find_one({"user_id": uid, "course_id": cid})

        completed_set = set(doc.get("completed_lessons", []))
        completed_set.add(lid)
        completed_list = list(completed_set)

        progress_pct = round((len(completed_list) / total_lessons) * 100, 1)
        if progress_pct > 100.0:
            progress_pct = 100.0
        is_completed = (len(completed_list) >= total_lessons)

        now = datetime.now(timezone.utc)
        collection.update_one(
            {"user_id": uid, "course_id": cid},
            {
                "$set": {
                    "completed_lessons": completed_list,
                    "last_lesson_id": lid,
                    "progress_percentage": progress_pct,
                    "is_completed": is_completed,
                    "updated_at": now
                }
            }
        )

        updated = collection.find_one({"user_id": uid, "course_id": cid})
        return serialize_doc(updated)

    @staticmethod
    def mark_lesson_uncompleted(user_id, course_id, lesson_id):
        collection = get_progress_collection()
        uid = str(user_id)
        cid = str(course_id)
        lid = str(lesson_id)

        course = CourseModel.find_by_id(cid)
        total_lessons = len(course.get("lessons", [])) if course else 1
        if total_lessons == 0:
            total_lessons = 1

        doc = collection.find_one({"user_id": uid, "course_id": cid})
        if not doc:
            return ProgressModel.get_or_create_progress(uid, cid)

        completed_set = set(doc.get("completed_lessons", []))
        completed_set.discard(lid)
        completed_list = list(completed_set)

        progress_pct = round((len(completed_list) / total_lessons) * 100, 1)
        is_completed = (len(completed_list) >= total_lessons)

        now = datetime.now(timezone.utc)
        collection.update_one(
            {"user_id": uid, "course_id": cid},
            {
                "$set": {
                    "completed_lessons": completed_list,
                    "progress_percentage": progress_pct,
                    "is_completed": is_completed,
                    "updated_at": now
                }
            }
        )

        updated = collection.find_one({"user_id": uid, "course_id": cid})
        return serialize_doc(updated)
