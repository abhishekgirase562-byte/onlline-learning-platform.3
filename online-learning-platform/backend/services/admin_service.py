from backend.models.user_model import UserModel
from backend.models.course_model import CourseModel, get_courses_collection
from backend.models.enrollment_model import EnrollmentModel
from backend.models.progress_model import ProgressModel

class AdminService:
    @staticmethod
    def get_stats():
        courses = CourseModel.get_courses()
        total_courses = len(courses)
        total_lessons = sum(len(c.get("lessons", [])) for c in courses)

        students = UserModel.get_all_users(role="student")
        total_students = len(students)

        enrollments = EnrollmentModel.get_all_enrollments()
        total_enrollments = len(enrollments)

        # Category breakdown
        category_counts = {}
        for c in courses:
            cat = c.get("category", "General")
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            "total_courses": total_courses,
            "total_students": total_students,
            "total_enrollments": total_enrollments,
            "total_lessons": total_lessons,
            "category_distribution": category_counts
        }

    @staticmethod
    def get_students():
        users = UserModel.get_all_users()
        students_data = []
        for u in users:
            uid = u.get("id")
            user_enrollments = EnrollmentModel.get_user_enrollments(uid)
            u_copy = dict(u)
            u_copy["enrollments_count"] = len(user_enrollments)
            students_data.append(u_copy)
        return students_data

    @staticmethod
    def get_enrollments():
        enrollments = EnrollmentModel.get_all_enrollments()
        detailed = []
        for enr in enrollments:
            uid = enr.get("user_id")
            cid = enr.get("course_id")

            user = UserModel.find_by_id(uid)
            course = CourseModel.find_by_id(cid)
            progress = ProgressModel.get_progress(uid, cid)

            detailed.append({
                "id": enr.get("id"),
                "user_id": uid,
                "student_name": user.get("name") if user else "Unknown User",
                "student_email": user.get("email") if user else "N/A",
                "course_id": cid,
                "course_title": course.get("title") if course else "Unknown Course",
                "enrolled_at": enr.get("enrolled_at"),
                "status": enr.get("status"),
                "progress_percentage": progress.get("progress_percentage", 0.0),
                "is_completed": progress.get("is_completed", False)
            })
        return detailed
