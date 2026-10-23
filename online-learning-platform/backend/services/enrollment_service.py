from backend.models.enrollment_model import EnrollmentModel
from backend.models.course_model import CourseModel
from backend.models.progress_model import ProgressModel

class EnrollmentService:
    @staticmethod
    def enroll(user_id, course_id):
        if not user_id:
            return None, "User authentication required"
        if not course_id:
            return None, "Course ID required"

        enrollment, err = EnrollmentModel.enroll_user(user_id, course_id)
        if err and "Already enrolled" in err:
            return enrollment, err
        if err:
            return None, err
        return enrollment, None

    @staticmethod
    def get_user_dashboard(user_id):
        enrollments = EnrollmentModel.get_user_enrollments(user_id)
        enrolled_courses = []

        total_completed_lessons = 0
        total_courses_completed = 0

        for enr in enrollments:
            cid = enr.get("course_id")
            course = CourseModel.find_by_id(cid)
            if not course:
                continue

            progress = ProgressModel.get_progress(user_id, cid)
            completed_lessons = progress.get("completed_lessons", [])
            total_completed_lessons += len(completed_lessons)

            if progress.get("is_completed", False):
                total_courses_completed += 1

            # Determine next lesson to continue learning
            lessons = course.get("lessons", [])
            next_lesson = None
            for lesson in lessons:
                if lesson.get("id") not in completed_lessons:
                    next_lesson = lesson
                    break
            if not next_lesson and lessons:
                next_lesson = lessons[0]

            enrolled_courses.append({
                "enrollment_id": enr.get("id"),
                "enrolled_at": enr.get("enrolled_at"),
                "course_id": cid,
                "title": course.get("title"),
                "slug": course.get("slug"),
                "category": course.get("category"),
                "difficulty": course.get("difficulty"),
                "thumbnail": course.get("thumbnail"),
                "instructor": course.get("instructor"),
                "total_lessons": len(lessons),
                "completed_lessons_count": len(completed_lessons),
                "progress_percentage": progress.get("progress_percentage", 0.0),
                "is_completed": progress.get("is_completed", False),
                "next_lesson_id": next_lesson.get("id") if next_lesson else None,
                "next_lesson_title": next_lesson.get("title") if next_lesson else None
            })

        total_enrolled = len(enrolled_courses)
        avg_progress = (
            round(sum(c["progress_percentage"] for c in enrolled_courses) / total_enrolled, 1)
            if total_enrolled > 0 else 0.0
        )

        return {
            "stats": {
                "total_enrolled": total_enrolled,
                "in_progress": total_enrolled - total_courses_completed,
                "completed_courses": total_courses_completed,
                "completed_lessons": total_completed_lessons,
                "average_progress": avg_progress
            },
            "enrolled_courses": enrolled_courses
        }

    @staticmethod
    def is_enrolled(user_id, course_id):
        return EnrollmentModel.is_enrolled(user_id, course_id)
