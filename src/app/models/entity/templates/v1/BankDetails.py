from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json
from pydantic import BaseModel, Field, conint


@dataclass_json
@dataclass
class BankDetails:
    account_number: Optional[str] = None
    ifsc: Optional[str] = None
    bank_name: Optional[str] = None
    branch_address: Optional[str] = None
    branch: Optional[str] = None

    def to_dict(self):
        return self.__dict__


class BankDetailsModel(BaseModel):
    account_number: conint(ge=100000000, le=999999999999999999)
    ifsc: str = Field(..., min_length=11, max_length=11)
    bank_name: str = Field(..., min_length=2)
    branch_address: str = Field(..., min_length=4)
    branch: str = Field(..., min_length=4)

    def to_dict(self):
        return self.__dict__
