from dataclasses import dataclass
from typing import Optional, Union

from dataclasses_json import dataclass_json
from pydantic import Field, BaseModel
from .....logs.logger import setup_logger

logger = setup_logger(__name__)

@dataclass_json
@dataclass
class Quantity:
    value: Optional[float] = None
    unit: Optional[str] = None

    def to_dict(self):
        return self.__dict__

    # @classmethod
    # def validate(
    #         cls,
    #         line_item: Dict,
    #         index: int = None,
    #         validation_errors: List[PydanticCustomError] = None
    # ) -> ValidatedField:
    #
    #     logger.info(f"Validating quantity model for line item at index {index}.")
    #
    #     actual_quantity_value = None
    #
    #     is_quantity_present = 'quantity' in line_item or line_item['quantity'] is not None and isinstance(line_item['quantity'], Dict)
    #     if is_quantity_present:
    #         logger.info(f"Quantity is present for line item at index {index}.")
    #         is_quantity_value_present = (
    #                 'value' in line_item['quantity'] or
    #                 line_item['quantity']['value'] is not None and
    #                 isinstance(line_item['quantity']['value'], Union[int, float])
    #         )
    #         if is_quantity_value_present:
    #             actual_quantity_value = line_item['quantity']['value']
    #             assumed_quantity_value = actual_quantity_value
    #             return ValidatedField(expected=assumed_quantity_value, actual=actual_quantity_value)
    #
    #     logger.info(f"Quantity is absent for line item at index {index}.")
    #     assumed_quantity_value = 1
    #     validation_errors.append(
    #         InvoiceValidationError(
    #             ValidationErrorType.ASSUMED_FIELD.value,
    #             f'Quantity value is not present or is invalid.',
    #             {
    #                 'error': '',
    #                 'assumed': assumed_quantity_value,
    #                 'actual': actual_quantity_value,
    #                 'loc': ('line_items', 'items', index, cls.__name__.lower())
    #             }
    #         )
    #     )
    #
    #     logger.info(f"Assumed quantity value for line item at index {index}: {assumed_quantity_value}.")
    #     return ValidatedField(expected=assumed_quantity_value, actual=actual_quantity_value)

class QuantityModel(BaseModel):
    value: Union[int, float] = Field(..., ge=0)
    unit: str = Field(..., min_length=1)

