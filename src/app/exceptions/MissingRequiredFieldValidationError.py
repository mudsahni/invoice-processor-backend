from typing import Optional, Any

from .ValidationErrorType import ValidationErrorType
from ..exceptions.BaseValidationError import BaseValidationError


class MissingRequiredFieldValidationError(BaseValidationError):

    def __init__(
            self,
            field: str,
            field_path: str,
            message: str = ""
    ):
        super().__init__(field, field_path, ValidationErrorType.MISSING_REQUIRED_FIELD, message)

    def __str__(self):
        return (f"{self.error_type} for field {self.field} in {self.field_path}. \n"
                f"{self.message}")
