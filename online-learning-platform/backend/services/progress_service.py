from backend.models.progress_model import ProgressModel
from backend.models.enrollment_model import EnrollmentModel

class ProgressService:
    @staticmethod
    def get_progress(user_id, course_id):
        return ProgressModel.get_progress(user_id, course_id)

    @staticmethod
    def complete_lesson(user_id, course_id, lesson_id):
        # Validate that user is enrolled (or auto-enroll if student)
        if not EnrollmentModel.is_enrolled(user_id, course_id):
            EnrollmentModel.enroll_user(user_id, course_id)
        return ProgressModel.mark_lesson_completed(user_id, course_id, lesson_id)

    @staticmethod
    def uncomplete_lesson(user_id, course_id, lesson_id):
        return ProgressModel.mark_lesson_uncompleted(user_id, course_id, lesson_id)
