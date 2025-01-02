from enum import Enum


class ValidationErrorType(Enum):
    MISSING_REQUIRED_FIELD = "missing-required-field"
    INVALID_FIELD_VALUE = "value_error"
    INVALID_FIELD_TYPE = "invalid-field-type"
    INVALID_FIELD_LENGTH = "invalid-field-length"
    INVALID_FIELD_RANGE = "invalid-field-range"
    INVALID_FIELD_PATTERN = "invalid-field-pattern"
    INVALID_FIELD_FORMAT = "invalid-field-format"
    INVALID_FIELD = "invalid-field"
    CALCULATED_FIELD = "calculated-field"
    ASSUMED_FIELD = "assumed-field"

    @classmethod
    def from_string(cls, value: str):
        if "missing" in value:
            return ValidationErrorType.MISSING_REQUIRED_FIELD
        if "value" in value:
            return ValidationErrorType.INVALID_FIELD_VALUE
        if "string" or "float" or "int" in value:
            return ValidationErrorType.INVALID_FIELD_TYPE

        return ValidationErrorType.INVALID_FIELD
