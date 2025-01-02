from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class InvoiceValidationFailure:

    failure_type: str
    message: str
    field: str

    def to_dict(self):
        return self.__dict__