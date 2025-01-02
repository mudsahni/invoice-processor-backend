from enum import Enum


class InvoiceParsingIntakeStatus(Enum):
    PROCESSING = 1
    SUCCESS = 2
    FAILURE = 3
    PENDING = 4
    CANCELLED = 5
