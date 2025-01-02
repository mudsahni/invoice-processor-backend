from dataclasses import dataclass
from typing import Optional, Union

from dataclasses_json import dataclass_json

from ....enum.TaxCategory import TaxCategory
from pydantic import BaseModel, Field

from .....logs.logger import setup_logger

logger = setup_logger(__name__)


@dataclass_json
@dataclass
class Tax:
    amount: Optional[float] = None
    category: Optional[TaxCategory] = None
    rate: Optional[float] = None

    def to_dict(self):
        return self.__dict__


class TaxModel(BaseModel):
    amount: Union[float, int] = Field(..., ge=0)
    category: str = Field(..., min_length=2)
    rate: Union[float, int] = Field(..., ge=0)
