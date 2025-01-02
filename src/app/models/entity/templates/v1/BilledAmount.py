from dataclasses import dataclass, field
from typing import Optional, Union

from dataclasses_json import dataclass_json

from .....models.entity.templates.v1.Tax import Tax, TaxModel
from pydantic import BaseModel, Field


@dataclass_json
@dataclass
class BilledAmount:
    amount_in_words: Optional[str] = None
    balance_due: Optional[float] = None
    sub_total: Optional[float] = None
    previous_dues: Optional[float] = None
    total: Optional[float] = None

    def to_dict(self):
        return self.__dict__

class BilledAmountModel(BaseModel):
    amount_in_words: str = Field(..., min_length=3)
    balance_due: Union[int, float] = Field(...)
    sub_total: Union[int, float] = Field(...)
    previous_dues: Union[int, float] = Field(...)
    total: Union[int, float] = Field(..., ge=0)

    # @model_validator(mode='before')
    # def check_total(cls, values):
    #     balance_due = values.get('balance_due')
    #     discount = values.get('discount')
    #     total = values.get('total')
    #
    #     if balance_due is not None and discount is not None and total is not None:
    #         # Check if the total is equal to balance_due - discount
    #         if balance_due != (total - discount):
    #             raise ValueError(f"Balance due must be equal to total - discount. Got {total} != {balance_due - discount}")
    #
    #     return values

    def to_dict(self):
        return self.__dict__
