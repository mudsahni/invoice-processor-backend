from ..exceptions.ValidationErrorType import ValidationErrorType


class BaseValidationError:

    def __init__(
            self,
            field: str,
            field_path: str,
            error_type: ValidationErrorType = ValidationErrorType.INVALID_FIELD_VALUE,
            message: str = ""
    ):
        self.field = field
        self.field_path = field_path
        self.error_type = error_type
        self.message = message

    def to_dict(self):
        return self.__dict__
