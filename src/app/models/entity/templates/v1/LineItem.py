from dataclasses import dataclass, field

from dataclasses_json import dataclass_json
from typing import Optional, Union

from .Discount import Discount, DiscountModel
from .Quantity import Quantity, QuantityModel
from .Tax import Tax, TaxModel
from pydantic import BaseModel, Field

from .....logs.logger import setup_logger

logger = setup_logger(__name__)


@dataclass_json
@dataclass
class LineItem:
    description: Optional[str] = None
    hsn_sac: Optional[int] = None
    quantity: Optional[Quantity] = None
    rate: Optional[float] = None
    amount: Optional[float] = None
    discount: Optional[Discount] = None
    taxes: Optional[list[Tax]] = field(default_factory=list)

    def to_dict(self):
        return self.__dict__

    # @classmethod
    # def _validate_rate(cls, line_item: Dict, index: int, validation_errors: List[InvoiceValidationError]) -> ValidatedField:
    #     logger.info(f"Validating rate for line item at index {index}.")
    #     assumed_rate = None
    #     actual_rate = None
    #     if 'rate' in line_item or line_item['rate'] is not None and isinstance(line_item['rate'], Union[int, float]):
    #         logger.info(f"Rate is present for line item at index {index}.")
    #         actual_rate = line_item['rate']
    #         assumed_rate = actual_rate
    #     else:
    #         logger.warn(f"Rate is absent for line item at index {index}.")
    #         validation_errors.append(
    #             InvoiceValidationError(
    #                 ValidationErrorType.CALCULATED_FIELD.value,
    #                 'Rate is not present or is invalid.',
    #                 {
    #                     'error': '',
    #                     'expected': assumed_rate,
    #                     'actual': actual_rate,
    #                     'loc': ('line_items', 'items', index, 'rate')
    #                 }
    #             )
    #         )
    #
    #     logger.info(f"Rate validation complete for line item at index {index}.")
    #     return ValidatedField(expected=assumed_rate, actual=actual_rate)
    #
    # @classmethod
    # def _validate_amount(cls, line_item: Dict, index: int, validation_errors: List[InvoiceValidationError]) -> ValidatedField:
    #     assumed_amount = None
    #     actual_amount = None
    #     if 'amount' in line_item or line_item['amount'] is not None and isinstance(line_item['amount'], Union[int, float]):
    #         logger.info(f"Amount is present for line item at index {index}.")
    #         actual_amount = line_item['amount']
    #         assumed_amount = actual_amount
    #     else:
    #         logger.error(f"Amount is absent for line item at index {index}.")
    #         validation_errors.append(
    #             InvoiceValidationError(
    #                 ValidationErrorType.CALCULATED_FIELD.value,
    #                 'Amount is not present or is invalid.',
    #                 {
    #                     'error': '',
    #                     'expected': assumed_amount,
    #                     'actual': actual_amount,
    #                     'loc': ('line_items', 'items', index, 'amount')
    #                 }
    #             )
    #         )
    #
    #     logger.info(f"Amount validation complete for line item at index {index}.")
    #     return ValidatedField(expected=assumed_amount, actual=actual_amount)
    #
    # @classmethod
    # def _validate_taxes(
    #         cls,
    #         line_item: Dict,
    #         discounted_amount: Union[int, float],
    #         index: int,
    #         validation_errors: List[InvoiceValidationError]
    # ) -> ValidatedField:
    #     tax_amounts = []
    #
    #     actual_total_tax_amount = None
    #     assumed_total_tax_amount = None
    #     if 'taxes' in line_item and line_item['taxes'] is not None and isinstance(line_item['taxes'], List):
    #         logger.info(f"Taxes are present for line item at index {index}.")
    #         for ix, tax in enumerate(line_item['taxes']):
    #             tax_amounts.append(Tax.validate(tax, discounted_amount, index, ix, validation_errors))
    #
    #         if all([tax.is_valid() == ValidationStatus.py.VALID for tax in tax_amounts]):
    #             logger.info(f"All taxes are valid for line item at index {index}.")
    #             actual_total_tax_amount = sum(tax_amount.expected for tax_amount in tax_amounts)
    #             assumed_total_tax_amount = actual_total_tax_amount
    #             return ValidatedField(expected=assumed_total_tax_amount, actual=actual_total_tax_amount)
    #
    #     logger.error(f"Taxes are absent or invalid for line item at index {index}.")
    #     assumed_total_tax_amount = 0
    #     validation_errors.append(
    #         InvoiceValidationError(
    #             ValidationErrorType.ASSUMED_FIELD.value,
    #             'Taxes are not present or are invalid.',
    #             {
    #                 'error': '',
    #                 'assumed': assumed_total_tax_amount,
    #                 'actual': actual_total_tax_amount,
    #                 'loc': ('line_items', 'items', index, 'taxes')
    #             }
    #         )
    #     )
    #
    #     logger.info(f"Tax validation complete for line item at index {index}.")
    #     return ValidatedField(expected=assumed_total_tax_amount, actual=actual_total_tax_amount)
    #
    # @classmethod
    # def validate(cls, line_item: Dict, index: int, validation_errors: List[Any]) -> ValidatedField:
    #
    #     logger.info(f"Validating line item at index {index}.")
    #
    #     rate = cls._validate_rate(line_item, index, validation_errors)
    #     amount = cls._validate_amount(line_item, index, validation_errors)
    #
    #     if rate.is_valid() != ValidationStatus.py.VALID and amount.is_valid() != ValidationStatus.py.VALID:
    #         logger.error(f"Rate and amount are absent for line item at index {index}.")
    #         # return line item amount as none
    #         return ValidatedField(expected=None, actual=None)
    #
    #     price = None
    #     if rate.is_valid() == ValidationStatus.py.VALID:
    #         logger.info(f"Rate is valid for line item at index {index}.")
    #         price = rate.expected
    #
    #     if amount.is_valid() == ValidationStatus.py.VALID and rate.is_valid() != ValidationStatus.py.VALID:
    #         logger.info(f"Amount is valid for line item at index {index} and rate is not valid.")
    #         # use amount in place of rate as rate is not defined
    #         # this means there will be no final comparison for line item between calculated amount and actual amount
    #         price = amount.expected
    #
    #
    #     quantity_value = Quantity.validate(line_item)
    #     if quantity_value.is_valid() == ValidationStatus.py.VALID:
    #         logger.info(f"Quantity is valid for line item at index {index}.")
    #         base_amount: int = quantity_value.actual * price
    #     else:
    #         logger.error(f"Quantity is absent or invalid for line item at index {index}.")
    #         base_amount: int = quantity_value.expected * price
    #
    #     logger.info(f"Base amount for line item at index {index}: {base_amount}.")
    #     discount_amount = Discount.validate(line_item, index, base_amount, validation_errors)
    #
    #
    #     # use case #1
    #     # using expected discounted amount, covers
    #         # discount amount is valid
    #         # discount amount did not exist but discount rate did
    #         # discount amount and rate both did not exist
    #         # discount amount and rate both exist but did not match
    #
    #     # there will always be a discount_amount.expected - either a real value or zero
    #
    #     discounted_amount_expected: int = base_amount - discount_amount.expected
    #     total_tax_amount_with_discounted_amount_expected = cls._validate_taxes(
    #         line_item,
    #         discounted_amount_expected,
    #         index,
    #         validation_errors
    #     )
    #
    #     # finding final amount with expected total tax
    #     final_amount_with_expected_discount_and_expected_tax: int = discounted_amount_expected + total_tax_amount_with_discounted_amount_expected.expected
    #
    #     if amount.is_valid() == ValidationStatus.py.VALID and rate.is_valid() == ValidationStatus.py.VALID:
    #         if abs(final_amount_with_expected_discount_and_expected_tax - amount.expected) <= COMPARISON_THRESHOLD * 100:
    #             logger.info(f"Final amount (expected discount, expected tax) matches expected amount for line item at index {index}.")
    #             return ValidatedField(expected=amount.expected, actual=final_amount_with_expected_discount_and_expected_tax)
    #
    #
    #     # finding final amount with actual total tax
    #     if total_tax_amount_with_discounted_amount_expected.actual is not None:
    #         final_amount_with_expected_discount_and_actual_tax = discounted_amount_expected + total_tax_amount_with_discounted_amount_expected.actual
    #
    #         if amount.is_valid() == ValidationStatus.py.VALID and rate.is_valid() == ValidationStatus.py.VALID:
    #             logger.info(f"Amount and rate are valid for line item at index {index}.")
    #             if abs(final_amount_with_expected_discount_and_actual_tax - amount.expected) <= COMPARISON_THRESHOLD * 100:
    #                 logger.info(f"Final amount (expected discount, actual tax) matches expected amount for line item at index {index}.")
    #                 return ValidatedField(expected=amount.expected, actual=final_amount_with_expected_discount_and_actual_tax)
    #
    #     # use case #2
    #     # when both discount amount and rate are present, but they don't match
    #     # covers
    #         # discount amount and rate both exist but did not match
    #     if discount_amount.is_valid() == ValidationStatus.py.INVALID:
    #         # second branch in case of invalid discount amount vs rate
    #         discounted_amount_actual = base_amount - discount_amount.actual
    #         total_tax_amount_with_discounted_amount_actual = cls._validate_taxes(
    #             line_item,
    #             discounted_amount_actual,
    #             index,
    #             validation_errors
    #         )
    #
    #         # finding final amount with expected total tax
    #         final_amount_with_actual_discount_and_expected_tax = discounted_amount_actual + total_tax_amount_with_discounted_amount_actual.expected
    #         if amount.is_valid() == ValidationStatus.py.VALID and rate.is_valid() == ValidationStatus.py.VALID:
    #             if rate.expected != amount.expected:
    #                 if abs(final_amount_with_actual_discount_and_expected_tax - amount.expected) <= COMPARISON_THRESHOLD * 100:
    #                     logger.info(f"Final amount (actual discount, expected tax) matches expected amount for line item at index {index}.")
    #                     return ValidatedField(expected=amount.expected, actual=final_amount_with_actual_discount_and_expected_tax)
    #
    #         # finding final amount with actual total tax
    #         if total_tax_amount_with_discounted_amount_actual.actual is not None:
    #             final_amount_with_actual_discount_and_actual_tax = discounted_amount_actual + total_tax_amount_with_discounted_amount_actual.actual
    #
    #             if amount.is_valid() == ValidationStatus.py.VALID and rate.is_valid() == ValidationStatus.py.VALID:
    #                 if rate.expected != amount.expected:
    #                     if abs(final_amount_with_actual_discount_and_actual_tax - amount.expected) <= COMPARISON_THRESHOLD * 100:
    #                         logger.info(f"Final amount (actual discount, actual tax) matches expected amount for line item at index {index}.")
    #                         return ValidatedField(expected=amount.expected, actual=final_amount_with_actual_discount_and_actual_tax)
    #
    #     logger.error(f"Final amount does not match expected amount for line item at index {index}.")
    #     validation_errors.append(
    #         InitErrorDetails(
    #             loc=('line_items', 'items', index),
    #             input=line_item,
    #             type=ValidationErrorType.INVALID_FIELD_VALUE.value,
    #             ctx={
    #                 'error': {
    #                     'msg': 'Final amount does not match expected amount',
    #                     'expected': amount.expected,
    #                     'actual': amount.actual
    #                 }
    #             }
    #         )
    #
    #     )
    #
    #     logger.info(f"Validation complete for line item at index {index}.")
    #     return ValidatedField(amount.expected, amount.actual)

class LineItemModel(BaseModel):
    description: str = Field(..., min_length=2)
    hsn_sac: int = Field(..., ge=2)
    quantity: QuantityModel = Field(...)
    rate: Union[int, float] = Field(..., ge=0)
    amount: Union[int, float] = Field(..., ge=0)
    discount: DiscountModel = Field(...)
    taxes: list[TaxModel] = Field(...)
