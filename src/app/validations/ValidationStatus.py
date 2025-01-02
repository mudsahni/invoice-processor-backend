from enum import Enum


class ValidationStatus(Enum):
    VALID = "valid"
    INVALID = "invalid"
    MISMATCH = "mismatch"
    ABSENT = "absent"
    NOT_APPLICABLE = "not-applicable"
    NOT_VALIDATED = 'not-validated'
    DERIVED = 'derived'
    CANNOT_BE_VALIDATED = "cannot-be-validated"
    MATCH = "match"

class FieldValidationStatus(Enum):
    VALID = "valid"
    INVALID = "invalid"
    ABSENT = "absent"
    NOT_VALIDATED = "not-validated"

class BusinessValidationStatus(Enum):
    MISMATCH = "mismatch"
    MATCH = "match"
    CANNOT_BE_VALIDATED = "cannot-be-validated"
    NOT_VALIDATED = "not-validated"
    DERIVED = "derived"
