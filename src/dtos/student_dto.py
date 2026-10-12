from models.student import Student
class StudentDTO:

    @staticmethod
    def only_obj_key(student: Student) -> dict:
        return {
            "student_key": student.student_key,
        }
