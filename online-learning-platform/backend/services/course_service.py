from backend.models.course_model import CourseModel
from backend.models.enrollment_model import EnrollmentModel
from backend.models.progress_model import ProgressModel

class CourseService:
    @staticmethod
    def list_courses(search=None, category=None, difficulty=None, featured_only=False, sort_by=None, limit=None):
        return CourseModel.get_courses(
            search=search,
            category=category,
            difficulty=difficulty,
            featured_only=featured_only,
            sort_by=sort_by,
            limit=limit
        )

    @staticmethod
    def get_course_details(course_id, current_user_id=None, is_admin=False):
        course = CourseModel.find_by_id(course_id)
        if not course:
            return None, "Course not found"

        is_enrolled = False
        progress = None

        if current_user_id:
            is_enrolled = EnrollmentModel.is_enrolled(current_user_id, course_id)
            if is_enrolled:
                progress = ProgressModel.get_progress(current_user_id, course_id)

        # Restrict protected lessons to enrolled students or admins
        has_access = is_enrolled or is_admin
        processed_lessons = []
        for l in course.get("lessons", []):
            lesson_copy = dict(l)
            # If not enrolled and not admin and not preview, lock lesson video URL
            if not has_access and not lesson_copy.get("is_preview", False):
                lesson_copy["video_url"] = None
                lesson_copy["is_locked"] = True
            else:
                lesson_copy["is_locked"] = False

            if progress and lesson_copy.get("id") in progress.get("completed_lessons", []):
                lesson_copy["is_completed"] = True
            else:
                lesson_copy["is_completed"] = False

            processed_lessons.append(lesson_copy)

        course["lessons"] = processed_lessons
        course["is_enrolled"] = is_enrolled
        course["progress"] = progress

        return course, None

    @staticmethod
    def create_course(data):
        return CourseModel.create_course(data)

    @staticmethod
    def update_course(course_id, data):
        return CourseModel.update_course(course_id, data)

    @staticmethod
    def delete_course(course_id):
        return CourseModel.delete_course(course_id)

    @staticmethod
    def add_lesson(course_id, lesson_data):
        return CourseModel.add_lesson(course_id, lesson_data)

    @staticmethod
    def update_lesson(course_id, lesson_id, lesson_data):
        return CourseModel.update_lesson(course_id, lesson_id, lesson_data)

    @staticmethod
    def delete_lesson(course_id, lesson_id):
        return CourseModel.delete_lesson(course_id, lesson_id)
