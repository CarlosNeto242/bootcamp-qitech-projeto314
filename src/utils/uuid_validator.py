import re

from errors import InvalidSchema

UUID_PATTERN = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def validate_uuid(value: str, field_name: str) -> str:
    if value is None or not UUID_PATTERN.match(value):
        raise InvalidSchema(f"{field_name} must be a valid UUID")

    return value
