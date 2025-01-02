from dataclasses import dataclass
from typing import Optional, Union

from dataclasses_json import dataclass_json
from pydantic import BaseModel, Field

from .....logs.logger import setup_logger

logger = setup_logger(__name__)

@dataclass_json
@dataclass
class Discount:
    percentage: Optional[float] = None
    amount: Optional[float] = None

    def to_dict(self):
        return self.__dict__

    # @classmethod
    # def validate(
    #         cls,
    #         line_item: Dict,
    #         index: int,
    #         base_amount: Union[int, float],
    #         validation_errors: List[InvoiceValidationError]
    # ) -> ValidatedField:
    #
    #     logger.info(f"Validating discount model for line item at index {index}.")
    #     actual_discount_percentage = None
    #     actual_discount_amount = None
    #     calculated_discount_amount = None
    #     calculated_discount_percentage = None
    #     # discount amount and discount percentage are both absent
    #     if 'discount' in line_item and line_item['discount'] is not None and isinstance(line_item['discount'], Dict):
    #         logger.info(f"Discount is present for line item at index {index}.")
    #         discount = line_item['discount']
    #         is_percentage_valid = (
    #                 'percentage' in discount and
    #                 discount['percentage'] is not None and
    #                 isinstance(discount['percentage'], Union[int, float])
    #         )
    #         is_amount_valid = (
    #                 'amount' in discount and
    #                 discount['amount'] is not None and
    #                 isinstance(discount['amount'], Union[int, float])
    #         )
    #         # discount percentage is present, discount amount is absent
    #         if is_percentage_valid and not is_amount_valid:
    #             logger.warn(f"Discount percentage is present but discount amount is absent for line item at index {index}.")
    #             actual_discount_percentage = discount['percentage'] / 100
    #             calculated_discount_amount = base_amount * actual_discount_percentage
    #             validation_errors.append(
    #                 InvoiceValidationError(
    #                     ValidationErrorType.CALCULATED_FIELD.value,
    #                     'Discount amount is not present or is invalid',
    #                     {
    #                         'error': '',
    #                         'expected': calculated_discount_amount,
    #                         'actual': actual_discount_amount,
    #                         'loc': ('line_items', 'items', index, cls.__name__.lower())
    #                     }
    #                 )
    #             )
    #         # discount amount is present, discount percentage is absent
    #         elif is_amount_valid and not is_percentage_valid:
    #             logger.warn(f"Discount amount is present but discount percentage is absent for line item at index {index}.")
    #             actual_discount_amount = discount['amount']
    #             calculated_discount_percentage = actual_discount_amount / base_amount
    #             validation_errors.append(
    #                 InvoiceValidationError(
    #                     ValidationErrorType.CALCULATED_FIELD.value,
    #                     'Discount percentage is not present or is invalid',
    #                     {
    #                         'error': '',
    #                         'expected': calculated_discount_percentage,
    #                         'actual': actual_discount_percentage,
    #                         'loc': ('line_items', 'items', index, cls.__name__.lower())
    #                     }
    #                 )
    #             )
    #         # both discount amount and percentage are present
    #         elif is_percentage_valid and is_amount_valid:
    #             logger.info(f"Discount percentage and discount amount are present for line item at index {index}.")
    #             actual_discount_percentage = discount['percentage'] / 100
    #             actual_discount_amount = discount['amount']
    #             calculated_discount_amount = base_amount * actual_discount_percentage
    #             calculated_discount_percentage = actual_discount_amount / base_amount
    #             # if either of the following dont match, and logically, if one doesnt match the other cant match either
    #             # we have two paths ahead of us, to try and run the rest of the calculations with discount amount
    #             # or with the calculated discount amount (i.e. based on percentage)
    #             if abs(calculated_discount_amount - actual_discount_amount) > COMPARISON_THRESHOLD:
    #                 logger.error(f"Discount amount does not match the calculated discount amount for line item at index {index}.")
    #                 validation_errors.append(
    #                     InvoiceValidationError(
    #                         ValidationErrorType.INVALID_FIELD_VALUE.value,
    #                         'Discount amount does not match the calculated discount amount',
    #                         {
    #                             'error': '',
    #                             'expected': calculated_discount_amount,
    #                             'actual': actual_discount_amount,
    #                             'loc': ('line_items', 'items', index, cls.__name__.lower(), 'amount')
    #                         }
    #
    #                     )
    #                 )
    #             if abs(calculated_discount_percentage - actual_discount_percentage) > COMPARISON_THRESHOLD:
    #                 logger.error(f"Discount percentage does not match the calculated discount percentage for line item at index {index}.")
    #                 validation_errors.append(
    #                     InvoiceValidationError(
    #                         ValidationErrorType.INVALID_FIELD_VALUE.value,
    #                         'Discount percentage does not match the calculated discount percentage',
    #                         {
    #                             'error': '',
    #                             'expected': calculated_discount_percentage,
    #                             'actual': actual_discount_percentage,
    #                             'loc': ('line_items', 'items', index, cls.__name__.lower(), 'percentage')
    #                         }
    #                     )
    #                 )
    #         else:
    #             logger.error(f"Discount percentage and amount are not present for line item at index {index}.")
    #             # since both discount percentage and amount are absent, we are assuming zero discount
    #             calculated_discount_amount = 0
    #             calculated_discount_percentage = 0
    #             validation_errors.extend(
    #                 [
    #                     InvoiceValidationError(
    #                         ValidationErrorType.ASSUMED_FIELD.value,
    #                         'Discount percentage is not present',
    #                         {
    #                             'error': '',
    #                             'assumed': calculated_discount_percentage,
    #                             'actual': actual_discount_percentage,
    #                             'loc': ('line_items', 'items', index, cls.__name__.lower())
    #                         }
    #                     ),
    #                     InvoiceValidationError(
    #                         ValidationErrorType.ASSUMED_FIELD.value,
    #                         'Discount amount is not present',
    #                         {
    #                             'error': '',
    #                             'assumed': calculated_discount_amount,
    #                             'actual': actual_discount_amount,
    #                             'loc': ('line_items', 'items', index, cls.__name__.lower())
    #                         }
    #                     )
    #                 ]
    #             )
    #     else:
    #         logger.error(f"Discount is absent for line item at index {index}.")
    #         # since both discount percentage and amount are absent, we are assuming zero discount
    #         calculated_discount_amount = 0
    #         calculated_discount_percentage = 0
    #         validation_errors.extend(
    #             [
    #                 InvoiceValidationError(
    #                     ValidationErrorType.ASSUMED_FIELD.value,
    #                     'Discount percentage is not present',
    #                     {
    #                         'error': '',
    #                         'assumed': calculated_discount_percentage,
    #                         'actual': actual_discount_percentage,
    #                         'loc': ('line_items', 'items', index, cls.__name__.lower())
    #                     }
    #                 ),
    #                 InvoiceValidationError(
    #                     ValidationErrorType.ASSUMED_FIELD.value,
    #                     'Discount amount is not present',
    #                     {
    #                         'error': '',
    #                         'assumed': calculated_discount_amount,
    #                         'actual': actual_discount_amount,
    #                         'loc': ('line_items', 'items', index, cls.__name__.lower())
    #                     }
    #                 )
    #             ]
    #         )
    #
    #     # either calculated will be populated or discount will be populated or both will be populated
    #     # there will be no case where both are none
    #     logger.info(f"Calculated discount amount for line item at index {index}: {calculated_discount_amount}.")
    #     return ValidatedField(expected=calculated_discount_amount, actual=actual_discount_amount)


class DiscountModel(BaseModel):
    percentage: Union[int, float] = Field(..., ge=0, le=100)
    amount: Union[int, float] = Field(..., ge=0)
