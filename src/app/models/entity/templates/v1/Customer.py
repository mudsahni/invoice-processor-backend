from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Optional
from pydantic import BaseModel, Field


@dataclass_json
@dataclass
class Customer:
    name: Optional[str] = None
    gst_number: Optional[str] = None
    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None
    pan: Optional[str] = None

    def to_dict(self):
        return self.__dict__


class CustomerModel(BaseModel):
    name: str = Field(..., min_length=2)
    gst_number: str = Field(..., min_length=15, max_length=15)
    billing_address: str = Field(..., min_length=4)
    shipping_address: str = Field(..., min_length=4)
    pan: str = Field(..., min_length=10)

    def to_dict(self):
        return self.__dict__
