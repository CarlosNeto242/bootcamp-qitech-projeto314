from fastapi import Request, Response
from fastapi import status as http_status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from controllers.student_controller import StudentController
from utils.schema_handler import SchemaHandler

DEFAULT_LIMIT = 10
DEFAULT_PAGE = 0


class StudentResource:
    @SchemaHandler.validate("post_student.json")
    def on_post(self, payload: dict) -> JSONResponse:
        controller = StudentController()
        student = controller.create(payload)

        return JSONResponse(
            content=jsonable_encoder(student),
            status_code=http_status.HTTP_201_CREATED,
        )
