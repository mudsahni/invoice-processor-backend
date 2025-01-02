from dataclasses import dataclass

from dataclasses_json import dataclass_json
from typing import Optional, List, Any

from pydantic_core import InitErrorDetails, PydanticCustomError

from .....models.entity.templates.v1.BilledAmount import BilledAmount, BilledAmountModel
from .....models.entity.templates.v1.Customer import Customer, CustomerModel
from .....models.entity.templates.v1.LineItem import LineItemModel, LineItem
from .....models.entity.templates.v1.Vendor import Vendor, VendorModel
from pydantic import BaseModel, Field, model_validator
from pydantic_core import ValidationError
from .....logs.logger import setup_logger

logger = setup_logger("parser model")


@dataclass_json
@dataclass
class ParsedInvoiceResponse:
    invoice_number: Optional[str] = None
    due_date: Optional[str] = None
    billing_date: Optional[str] = None
    place_of_supply: Optional[str] = None
    customer: Optional[Customer] = None
    vendor: Optional[Vendor] = None
    line_items: Optional[List[LineItem]] = None
    billed_amount: Optional[BilledAmount] = None
    currency_code: Optional[str] = None

    def to_dict(self):
        return self.__dict__



class ParsedInvoiceResponseModel(BaseModel):
    invoice_number: str = Field(..., min_length=1)
    due_date: str = Field(..., min_length=1)
    billing_date: str = Field(..., min_length=1)
    place_of_supply: str = Field(..., min_length=1)
    customer: CustomerModel = Field(...)
    vendor: VendorModel = Field(...)
    line_items: List[LineItemModel] = Field(..., min_items=1)
    billed_amount: BilledAmountModel
    currency_code: str = Field(..., min_length=2)