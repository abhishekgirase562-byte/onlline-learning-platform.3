import uuid
from datetime import datetime, timezone
import re
from backend.config import get_db
from backend.models.utils import serialize_doc, to_object_id

def get_courses_collection():
    return get_db()["courses"]

def generate_slug(title):
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    return re.sub(r"[-\s]+", "-", slug).strip("-")


class CourseModel:
    @staticmethod
    def get_courses(search=None, category=None, difficulty=None, featured_only=False, sort_by=None, limit=None):
        collection = get_courses_collection()
        query = {}

        if search:
            # Case-insensitive title/description/category search
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"short_description": {"$regex": search, "$options": "i"}},
                {"category": {"$regex": search, "$options": "i"}},
                {"instructor.name": {"$regex": search, "$options": "i"}}
            ]

        if category and category.lower() != "all":
            query["category"] = {"$regex": f"^{re.escape(category)}$", "$options": "i"}

        if difficulty and difficulty.lower() != "all":
            query["difficulty"] = {"$regex": f"^{re.escape(difficulty)}$", "$options": "i"}

        if featured_only:
            query["featured"] = True

        cursor = collection.find(query)

        # Sorting
        if sort_by == "highest_rated":
            cursor = cursor.sort("rating", -1)
        elif sort_by == "newest":
            cursor = cursor.sort("created_at", -1)
        elif sort_by == "price_low":
            cursor = cursor.sort("price", 1)
        elif sort_by == "price_high":
            cursor = cursor.sort("price", -1)
        else:
            # Default sort: featured first, then enrollment count
            cursor = cursor.sort([("featured", -1), ("students_enrolled", -1), ("created_at", -1)])

        if limit and limit > 0:
            cursor = cursor.limit(limit)

        courses = list(cursor)
        return [serialize_doc(c) for c in courses]

    @staticmethod
    def find_by_id(course_id):
        collection = get_courses_collection()
        oid = to_object_id(course_id)
        if not oid:
            return None
        doc = collection.find_one({"_id": oid})
        return serialize_doc(doc) if doc else None

    @staticmethod
    def find_by_slug(slug):
        collection = get_courses_collection()
        doc = collection.find_one({"slug": slug.strip().lower()})
        return serialize_doc(doc) if doc else None

    @staticmethod
    def create_course(data):
        collection = get_courses_collection()
        now = datetime.now(timezone.utc)

        title = data.get("title", "").strip()
        if not title:
            return None, "Title is required"

        slug = data.get("slug") or generate_slug(title)
        # Check uniqueness of slug
        existing = collection.find_one({"slug": slug})
        if existing:
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"

        lessons = data.get("lessons", [])
        # Assign IDs to lessons if missing
        for idx, lesson in enumerate(lessons, start=1):
            if "id" not in lesson:
                lesson["id"] = f"lesson-{uuid.uuid4().hex[:8]}"
            if "order" not in lesson:
                lesson["order"] = idx

        course_doc = {
            "title": title,
            "slug": slug,
            "category": data.get("category", "General"),
            "difficulty": data.get("difficulty", "Beginner"),
            "duration": data.get("duration", "4h 00m"),
            "price": float(data.get("price", 0.0)),
            "thumbnail": data.get("thumbnail", "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80"),
            "short_description": data.get("short_description", title),
            "description": data.get("description", ""),
            "learning_objectives": data.get("learning_objectives", []),
            "requirements": data.get("requirements", []),
            "featured": bool(data.get("featured", False)),
            "rating": float(data.get("rating", 4.8)),
            "reviews_count": int(data.get("reviews_count", 0)),
            "students_enrolled": int(data.get("students_enrolled", 0)),
            "instructor": data.get("instructor", {
                "name": "LearnHub Instructor",
                "title": "Senior Educator",
                "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Instructor",
                "bio": "Experienced software engineer and educator."
            }),
            "lessons": lessons,
            "created_at": now,
            "updated_at": now
        }

        result = collection.insert_one(course_doc)
        course_doc["_id"] = result.inserted_id
        return serialize_doc(course_doc), None

    @staticmethod
    def update_course(course_id, data):
        collection = get_courses_collection()
        oid = to_object_id(course_id)
        if not oid:
            return None, "Invalid course ID"

        existing = collection.find_one({"_id": oid})
        if not existing:
            return None, "Course not found"

        update_fields = {"updated_at": datetime.now(timezone.utc)}

        allowed_fields = [
            "title", "slug", "category", "difficulty", "duration", "price",
            "thumbnail", "short_description", "description", "learning_objectives",
            "requirements", "featured", "rating", "reviews_count", "instructor", "lessons"
        ]

        for field in allowed_fields:
            if field in data:
                if field == "price":
                    update_fields[field] = float(data[field])
                elif field == "featured":
                    update_fields[field] = bool(data[field])
                elif field == "lessons":
                    lessons = data[field]
                    for idx, l in enumerate(lessons, start=1):
                        if "id" not in l:
                            l["id"] = f"lesson-{uuid.uuid4().hex[:8]}"
                        if "order" not in l:
                            l["order"] = idx
                    update_fields["lessons"] = lessons
                else:
                    update_fields[field] = data[field]

        collection.update_one({"_id": oid}, {"$set": update_fields})
        updated = collection.find_one({"_id": oid})
        return serialize_doc(updated), None

    @staticmethod
    def delete_course(course_id):
        collection = get_courses_collection()
        oid = to_object_id(course_id)
        if not oid:
            return False
        res = collection.delete_one({"_id": oid})
        return res.deleted_count > 0

    @staticmethod
    def add_lesson(course_id, lesson_data):
        collection = get_courses_collection()
        oid = to_object_id(course_id)
        if not oid:
            return None, "Invalid course ID"

        course = collection.find_one({"_id": oid})
        if not course:
            return None, "Course not found"

        existing_lessons = course.get("lessons", [])
        lesson_id = lesson_data.get("id") or f"lesson-{uuid.uuid4().hex[:8]}"

        new_lesson = {
            "id": lesson_id,
            "title": lesson_data.get("title", "New Lesson").strip(),
            "description": lesson_data.get("description", "").strip(),
            "duration": lesson_data.get("duration", "10:00").strip(),
            "video_url": lesson_data.get("video_url", "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"),
            "order": len(existing_lessons) + 1,
            "is_preview": bool(lesson_data.get("is_preview", False))
        }

        collection.update_one(
            {"_id": oid},
            {
                "$push": {"lessons": new_lesson},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            }
        )
        return new_lesson, None

    @staticmethod
    def update_lesson(course_id, lesson_id, lesson_data):
        collection = get_courses_collection()
        oid = to_object_id(course_id)
        if not oid:
            return None, "Invalid course ID"

        course = collection.find_one({"_id": oid})
        if not course:
            return None, "Course not found"

        lessons = course.get("lessons", [])
        found = False
        for l in lessons:
            if l.get("id") == lesson_id:
                found = True
                if "title" in lesson_data:
                    l["title"] = lesson_data["title"].strip()
                if "description" in lesson_data:
                    l["description"] = lesson_data["description"].strip()
                if "duration" in lesson_data:
                    l["duration"] = lesson_data["duration"].strip()
                if "video_url" in lesson_data:
                    l["video_url"] = lesson_data["video_url"].strip()
                if "is_preview" in lesson_data:
                    l["is_preview"] = bool(lesson_data["is_preview"])
                break

        if not found:
            return None, "Lesson not found"

        collection.update_one(
            {"_id": oid},
            {"$set": {"lessons": lessons, "updated_at": datetime.now(timezone.utc)}}
        )
        return l, None

    @staticmethod
    def delete_lesson(course_id, lesson_id):
        collection = get_courses_collection()
        oid = to_object_id(course_id)
        if not oid:
            return False, "Invalid course ID"

        collection.update_one(
            {"_id": oid},
            {
                "$pull": {"lessons": {"id": lesson_id}},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            }
        )
        return True, None

    @staticmethod
    def increment_enrollment(course_id, delta=1):
        collection = get_courses_collection()
        oid = to_object_id(course_id)
        if oid:
            collection.update_one({"_id": oid}, {"$inc": {"students_enrolled": delta}})
