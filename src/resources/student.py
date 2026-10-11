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
        sample_entity = controller.create(payload)

        return JSONResponse(
            content=jsonable_encoder(sample_entity),
            status_code=http_status.HTTP_201_CREATED,
        )

    def on_get_by_key(self, sample_entity_key: str) -> JSONResponse:
        controller = StudentController()
        sample_entity = controller.get_by_key(sample_entity_key)

        return JSONResponse(
            content=jsonable_encoder(sample_entity),
            status_code=http_status.HTTP_200_OK,
        )

    @SchemaHandler.validate("put_sample_entity.json")
    def on_put_by_key(self, sample_entity_key: str, payload: dict) -> JSONResponse:
        controller = StudentController()
        sample_entity = controller.update_status(sample_entity_key, payload["status"])

        return JSONResponse(
            content=jsonable_encoder(sample_entity),
            status_code=http_status.HTTP_202_ACCEPTED,
        )

    def on_put_increment_counter(self, sample_entity_key: str) -> Response:
        controller = StudentController()
        controller.webhook_increment_counter(sample_entity_key)
        return Response(status_code=http_status.HTTP_204_NO_CONTENT)

    @SchemaHandler.validate_query_params("get_sample_entities.json")
    def on_get_list(self, request: Request) -> JSONResponse:

        controller = StudentController()

        query_params = request.query_params

        limit = int(query_params.get("limit", DEFAULT_LIMIT))
        page = int(query_params.get("page", DEFAULT_PAGE))

        filters = {
            "status_enumerators": query_params.getlist("status"),
            "name": query_params.get("name"),
            "email": query_params.get("email"),
            "document_number": query_params.get("document_number"),
            "birthdate_from": query_params.get("birthdate_from"),
            "birthdate_to": query_params.get("birthdate_to"),
        }

        offset = page * limit
        sample_entities_page = controller.get_list(limit, offset, filters)

        page_envelope = {
            "data": sample_entities_page["sample_entities_list_dto"],
            "limit": limit,
            "page": page,
            "is_last_page": sample_entities_page["is_last_page"],
        }

        return JSONResponse(
            content=jsonable_encoder(page_envelope),
            status_code=http_status.HTTP_200_OK,
        )
