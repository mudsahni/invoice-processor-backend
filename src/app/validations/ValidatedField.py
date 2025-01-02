from dataclasses import dataclass
from dataclasses import field as field_type
from typing import List, Any

from .ValidationError import ValidationError
from .ValidationStatus import BusinessValidationStatus, FieldValidationStatus


@dataclass
class ValidatedFieldValue:
    actual: Any
    expected: Any

    def to_dict(self):
        return self.__dict__

@dataclass
class ValidatedField:
    field: str
    errors: List[ValidationError]
    value: ValidatedFieldValue
    notes: List[str] = field_type(default_factory=list)
    field_validation_status: FieldValidationStatus = FieldValidationStatus.NOT_VALIDATED
    business_validation_status: BusinessValidationStatus = BusinessValidationStatus.NOT_VALIDATED

    def to_dict(self):
        return {
            'field': self.field,
            'errors': [error.to_dict() for error in self.errors],
            'field_validation_status': self.field_validation_status.value,
            'business_validation_status': self.business_validation_status.value,
            'value': self.value.to_dict(),
            'notes': self.notes
        }
