from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from .....models.entity.templates.v1.BankDetails import BankDetails, BankDetailsModel
from pydantic import BaseModel, Field


@dataclass_json
@dataclass
class Vendor:
    name: Optional[str] = None
    address: Optional[str] = None
    bank_details: Optional[BankDetails] = None
    gst_number: Optional[str] = None
    pan: Optional[str] = None
    upi_id: Optional[str] = None

    def to_dict(self):
        return self.__dict__

class VendorModel(BaseModel):
    name: str = Field(..., min_length=2)
    address: str = Field(..., min_length=4)
    bank_details: BankDetailsModel = Field(...)
    gst_number: str = Field(..., min_length=15, max_length=15)
    pan: str = Field(..., min_length=10, max_length=10)
    upi_id: str = Field(..., min_length=5)

    def to_dict(self):
        return self.__dict__
