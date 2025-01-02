from dataclasses import dataclass
from enum import Enum

from .ValidationType import ValidationType


class ValidationErrorLevel(Enum):
    MAJOR = 'major'
    MINOR = 'minor'

    @classmethod
    def get_level(cls, required: bool):
        if required:
            return ValidationErrorLevel.MAJOR
        return ValidationErrorLevel.MINOR
@dataclass
class ValidationError:

    error_level: ValidationErrorLevel
    validation_type: ValidationType
    message: str

    def to_dict(self):
        return {
            'error_level': self.error_level.value,
            'validation_type': self.validation_type.value,
            'message': self.message
        }
