from typing import Optional, Any

from .ValidationErrorType import ValidationErrorType
from ..exceptions.BaseValidationError import BaseValidationError


class ValidationError(BaseValidationError):

    def __init__(
            self,
            field: str,
            field_path: str,
            message: str = "",
            calculated_value: Optional[Any] = None,
            actual_value: Optional[Any] = None
    ):
        super().__init__(field, field_path, ValidationErrorType.INVALID_FIELD_VALUE, message)
        self.calculated_value = calculated_value
        self.actual_value = actual_value

    def __str__(self):
        return (f"{self.error_type} for field {self.field} in {self.field_path}. \n"
                f"Calculated {self.calculated_value}, Actual {self.actual_value} \n"
                f"{self.message}")
