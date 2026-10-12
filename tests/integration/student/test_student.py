import re
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from tests.utils import ObjectGenerator, PayloadGenerator, RequestGenerator
from tests.utils.mock_generator import UniversityMock

UUID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


class TestStudent:
    def test_refuses_malformed_body(self):
        valid_payload = PayloadGenerator.create_student_payload()

        malformed_payloads = [
            ("corpo vazio", {}),
            ("sem name", {"document_number": valid_payload["document_number"]}),
            ("sem document_number", {"name": valid_payload["name"]}),
            ("campo extra", {**valid_payload, "campo_extra": 1}),
            ("name vazio", {**valid_payload, "name": ""}),
            ("name acima de 255 caracteres", {**valid_payload, "name": "a" * 256}),
            ("CPF sem mascara", {**valid_payload, "document_number": "52998224725"}),
            ("CPF com mascara errada", {**valid_payload, "document_number": "529.982.24725"}),
        ]

        for case, payload in malformed_payloads:
            status, response = RequestGenerator.POST_student(payload)

            assert status == 400, f"{case}: status {status}"
            assert response["code"] == "QIT000001", f"{case}: code {response['code']}"

    def test_creates_student(self):
        payload = PayloadGenerator.create_student_payload()
        UniversityMock.GET_university_student(payload["document_number"])

        status, response = RequestGenerator.POST_student(payload)

        assert status == 201
        assert UUID_PATTERN.match(response["student_key"])
        assert ObjectGenerator.count_students(payload["document_number"]) == 1

    def test_refuses_student_not_recognized_by_university(self):
        payload = PayloadGenerator.create_student_payload()
        UniversityMock.GET_university_student_not_found(payload["document_number"])

        status, response = RequestGenerator.POST_student(payload)

        assert status == 422
        assert response["code"] == "QIT001003"
        assert ObjectGenerator.count_students(payload["document_number"]) == 0

    def test_refuses_duplicated_document_number(self):
        payload = PayloadGenerator.create_student_payload()
        UniversityMock.GET_university_student(payload["document_number"])

        first_status, _ = RequestGenerator.POST_student(payload)
        second_status, second_response = RequestGenerator.POST_student(payload)

        assert first_status == 201
        assert second_status == 409
        assert second_response["code"] == "QIT001004"
        assert ObjectGenerator.count_students(payload["document_number"]) == 1

    def test_university_check_comes_before_duplicated_document_number(self):
        payload = PayloadGenerator.create_student_payload()
        UniversityMock.GET_university_student(payload["document_number"])

        status, _ = RequestGenerator.POST_student(payload)
        assert status == 201

        UniversityMock.GET_university_student_not_found(payload["document_number"])

        status, response = RequestGenerator.POST_student(payload)

        assert status == 422
        assert response["code"] == "QIT001003"

    def test_university_connection_dropped_returns_unavailable(self):
        payload = PayloadGenerator.create_student_payload()
        UniversityMock.GET_university_student_connection_dropped(payload["document_number"])

        status, response = RequestGenerator.POST_student(payload)

        assert status == 503
        assert response["code"] == "QIT001014"
        assert ObjectGenerator.count_students(payload["document_number"]) == 0

    def test_university_timeout_returns_unavailable(self):
        payload = PayloadGenerator.create_student_payload()
        UniversityMock.GET_university_student_timeout(payload["document_number"])

        status, response = RequestGenerator.POST_student(payload)

        assert status == 503
        assert response["code"] == "QIT001014"
        assert ObjectGenerator.count_students(payload["document_number"]) == 0

    def test_university_server_error_returns_unavailable(self):
        payload = PayloadGenerator.create_student_payload()
        UniversityMock.GET_university_student_server_error(payload["document_number"])

        status, response = RequestGenerator.POST_student(payload)

        assert status == 503
        assert response["code"] == "QIT001014"
        assert ObjectGenerator.count_students(payload["document_number"]) == 0

    def test_simultaneous_same_document_number_only_one_passes(self):
        payload = PayloadGenerator.create_student_payload()
        UniversityMock.GET_university_student(payload["document_number"])
        barrier = Barrier(2)

        def send(_):
            barrier.wait()
            return RequestGenerator.POST_student(payload)

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(send, range(2)))

        statuses = sorted(status for status, _ in results)
        codes = [response["code"] for status, response in results if status == 409]

        assert statuses == [201, 409]
        assert codes == ["QIT001004"]
        assert ObjectGenerator.count_students(payload["document_number"]) == 1
