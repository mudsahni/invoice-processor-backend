from typing import Dict, List, Union, Type, Tuple

from .ValidatedField import ValidatedField, ValidatedFieldValue
from .ValidationError import ValidationError, ValidationErrorLevel
from .ValidationStatus import ValidationStatus, FieldValidationStatus, BusinessValidationStatus
from .ValidationType import ValidationType
from ..logs.logger import setup_logger

logger = setup_logger(__name__)


def validate_field_presence(data: Dict, field: str) -> bool:
    if field not in data or data[field] is None or data[field] == '':
        return False

    return True


def validate_field_type(data: Dict, field: str, expected_type: Type) -> bool:
    if not isinstance(data[field], expected_type):
        return False

    return True


def validate_field_range(
        data: Dict,
        field: str,
        min_value: Union[float, int, None],
        max_value: Union[float, int, None]
) -> bool:
    value = data[field]
    if isinstance(data[field], (str, list, dict)):
        value = len(data[field])

    if min_value is not None and value < min_value:
        return False
    if max_value is not None and value > max_value:
        return False

    return True


def validate_field_pattern(data: Dict, field: str, pattern: str) -> bool:
    import re
    if not re.match(pattern, data[field]):
        return False

    return True


def validate_field(data: Dict, field_name: str, field_config: Dict):
    validated_field = ValidatedField(
        field=field_name,
        errors=[],
        value=ValidatedFieldValue(
            actual=None,
            expected=None
        )
    )

    error_level = ValidationErrorLevel.get_level(field_config['required'])

    if not validate_field_presence(data, field_name):
        validated_field.field_validation_status = FieldValidationStatus.ABSENT
        validated_field.errors.append(
            ValidationError(
                error_level=error_level,
                validation_type=ValidationType.PRESENCE,
                message=f'{field_name} is absent'
            )
        )
        return validated_field

    if not validate_field_type(data, field_name, field_config['type']):
        validated_field.field_validation_status = FieldValidationStatus.INVALID
        validated_field.value.actual = type(data[field_name])
        validated_field.value.expected = field_config['type']
        validated_field.errors.append(
            ValidationError(
                error_level=error_level,
                validation_type=ValidationType.TYPE,
                message=f'{field_name} is not of type {field_config["type"].__name__}'
            )
        )
        return validated_field

    if 'range' in field_config and field_config['range'] is not None and not validate_field_range(data, field_name,
                                                                                                  field_config['range'][
                                                                                                      0],
                                                                                                  field_config['range'][
                                                                                                      1]):
        validated_field.field_validation_status = FieldValidationStatus.INVALID
        validated_field.value.actual = len(data[field_name])
        validated_field.value.expected = field_config['range']
        validated_field.errors.append(
            ValidationError(
                error_level=error_level,
                validation_type=ValidationType.RANGE,
                message=f'{field_name} range is not in range {field_config["range"]}'
            )
        )
        return validated_field

    if 'pattern' in field_config and field_config['pattern'] is not None and not validate_field_pattern(data,
                                                                                                        field_name,
                                                                                                        field_config[
                                                                                                            'pattern']):
        validated_field.field_validation_status = FieldValidationStatus.INVALID
        validated_field.value.actual = data[field_name]
        validated_field.value.expected = field_config['pattern']
        validated_field.errors.append(
            ValidationError(
                error_level=error_level,
                validation_type=ValidationType.PATTERN,
                message=f'{field_name} does not match pattern {field_config["pattern"]}'
            )
        )
        return validated_field

    # if 'business' in field_config:
    #     return validated_field

    validated_field.field_validation_status = FieldValidationStatus.VALID
    validated_field.value.actual = data[field_name]
    return validated_field


def customer_validation(customer: Dict) -> Dict[str, Dict]:
    from .ValidationConfig import customer as customer_config

    validated_fields: Dict[str, Dict] = {}

    for field_name, field_config in customer_config['fields'].items():
        validated_field = validate_field(customer, field_name, field_config)
        validated_fields[field_name] = validated_field.to_dict()

    # do the customer business validations if required
    return validated_fields


def billed_amount_validation(billed_amount: Dict):
    from .ValidationConfig import billed_amount as billed_amount_config

    validated_fields: Dict[str, Dict] = {}

    for field_name, field_config in billed_amount_config['fields'].items():
        validated_field = validate_field(billed_amount, field_name, field_config)
        validated_fields[field_name] = validated_field.to_dict()

    # do the customer business validations if required
    return validated_fields


def vendor_validation(vendor: Dict):
    from .ValidationConfig import vendor as vendor_config
    from .ValidationConfig import bank_details as bank_details_config

    vendor_validated_fields: Dict[str, Union[Dict, List]] = {}

    for field_name, field_config in vendor_config['fields'].items():
        validated_field = validate_field(vendor, field_name, field_config)
        vendor_validated_fields[field_name] = validated_field.to_dict()

    if vendor_validated_fields['bank_details']['field_validation_status'] == FieldValidationStatus.VALID.value:
        bank_details_validated_fields: Dict[str, Dict] = {}
        for field_name, field_config in bank_details_config['fields'].items():
            validated_field = validate_field(vendor['bank_details'], field_name, field_config)
            bank_details_validated_fields[field_name] = validated_field.to_dict()
        vendor_validated_fields['bank_details'] = bank_details_validated_fields

    # do the customer business validations if required
    return vendor_validated_fields


def quantity_validation(quantity: Dict) -> Tuple[Union[int, float, None], Dict[str, Dict]]:
    from .ValidationConfig import quantity as quantity_config

    validated_fields: Dict[str, Dict] = {}

    for field_name, field_config in quantity_config['fields'].items():
        validated_field = validate_field(quantity, field_name, field_config)
        validated_fields[field_name] = validated_field.to_dict()

    if validated_fields['value']['field_validation_status'] != FieldValidationStatus.VALID.value:
        validated_fields['value']['notes'].append("Line item quantity could not be validated. Assuming as one.")
        return 1, validated_fields

    return quantity['value'], validated_fields


def discount_validation(discount: Dict, item_rate: Union[int, float]) -> Tuple[Tuple, Dict[str, Dict]]:
    from .ValidationConfig import discount as discount_config

    validated_fields: Dict[str, Dict] = {}

    for field_name, field_config in discount_config['fields'].items():
        validated_field = validate_field(discount, field_name, field_config)
        validated_fields[field_name] = validated_field.to_dict()

    is_amount_valid = validated_fields['amount']['field_validation_status'] == FieldValidationStatus.VALID.value
    is_percentage_valid = validated_fields['percentage']['field_validation_status'] == FieldValidationStatus.VALID.value

    # if percentage and amount are both valid
    if is_percentage_valid and is_amount_valid:

        actual_discount_amount = discount['amount']
        actual_discount_percentage = discount['percentage']

        expected_discount_amount = item_rate * (actual_discount_percentage / 100)

        expected_discount_percentage = (actual_discount_amount / item_rate) * 100

        if abs(actual_discount_amount - expected_discount_amount) > 0.01:
            validated_fields['amount']['business_validation_status'] = BusinessValidationStatus.MISMATCH.value
            validated_fields['amount']['value']['expected'] = expected_discount_amount
            validated_fields['amount']['errors'].append(
                ValidationError(
                    error_level=ValidationErrorLevel.MAJOR,
                    validation_type=ValidationType.BUSINESS,
                    message=f'Discount amount {actual_discount_amount} is not equal to {expected_discount_amount}'
                ).to_dict()
            )
        else:
            validated_fields['amount']['business_validation_status'] = BusinessValidationStatus.MATCH.value
            validated_fields['amount']['value']['expected'] = expected_discount_amount

        if abs(actual_discount_percentage - expected_discount_percentage) > 0.01:
            validated_fields['percentage']['business_validation_status'] = BusinessValidationStatus.MISMATCH.value
            validated_fields['percentage']['value']['expected'] = expected_discount_percentage
            validated_fields['percentage']['errors'].append(
                ValidationError(
                    error_level=ValidationErrorLevel.MAJOR,
                    validation_type=ValidationType.BUSINESS,
                    message=f'Discount rate {actual_discount_percentage} is not equal to {expected_discount_percentage}'
                ).to_dict()
            )
        else:
            validated_fields['percentage']['business_validation_status'] = BusinessValidationStatus.MATCH.value
            validated_fields['percentage']['value']['expected'] = expected_discount_percentage

        return (actual_discount_amount, expected_discount_amount), validated_fields

    elif is_percentage_valid and not is_amount_valid:
        expected_discount_amount = item_rate * (discount['percentage'] / 100)

        validated_fields['percentage']['business_validation_status'] = (
            BusinessValidationStatus.CANNOT_BE_VALIDATED.value)
        validated_fields['amount']['business_validation_status'] = BusinessValidationStatus.DERIVED.value
        validated_fields['amount']['value']['expected'] = expected_discount_amount
        validated_fields['amount']['notes'].append(
            'Discount amount was absent/invalid. Derived discount amount from discount percentage.'
        )

        return (None, expected_discount_amount), validated_fields

    elif is_amount_valid and not is_percentage_valid:
        expected_discount_percentage = (discount['amount'] / item_rate) * 100

        validated_fields['amount']['business_validation_status'] = BusinessValidationStatus.CANNOT_BE_VALIDATED.value
        validated_fields['percentage']['business_validation_status'] = BusinessValidationStatus.DERIVED.value
        validated_fields['percentage']['value']['expected'] = expected_discount_percentage
        validated_fields['percentage']['notes'].append(
            'Discount percentage was absent/invalid. Derived discount percentage from discount amount.'
        )

        return (discount['amount'], None), validated_fields
    else:
        logger.info("Both discount amount and percentage are missing. Assuming no discount.")

        validated_fields['amount']['business_validation_status'] = BusinessValidationStatus.DERIVED.value
        validated_fields['amount']['value']['expected'] = 0
        validated_fields['amount']['notes'].append(
            'Discount amount was absent/invalid. Assuming discount amount to be zero.'
        )
        validated_fields['percentage']['business_validation_status'] = BusinessValidationStatus.DERIVED.value
        validated_fields['percentage']['value']['expected'] = 0
        validated_fields['percentage']['notes'].append(
            'Discount percentage was absent/invalid. Assuming discount percentage to be zero.'
        )

        return (0, 0), validated_fields


def tax_validation(tax: Dict, taxable_amount: Union[int, float]) -> Tuple[Tuple, Dict[str, Dict]]:
    from .ValidationConfig import tax as tax_config

    validated_fields: Dict[str, Dict] = {}

    for field_name, field_config in tax_config['fields'].items():
        validated_field = validate_field(tax, field_name, field_config)
        validated_fields[field_name] = validated_field.to_dict()

    is_amount_valid = validated_fields['amount']['field_validation_status'] == FieldValidationStatus.VALID.value
    is_rate_valid = validated_fields['rate']['field_validation_status'] == FieldValidationStatus.VALID.value

    if is_amount_valid and is_rate_valid:
        actual_tax_amount = tax['amount']
        expected_tax_amount = taxable_amount * tax['rate'] / 100

        actual_tax_rate = tax['rate']
        expected_tax_rate = tax['amount'] / taxable_amount * 100

        if abs(actual_tax_amount - expected_tax_amount) > 0.01:
            validated_fields['amount']['business_validation_status'] = BusinessValidationStatus.MISMATCH.value
            validated_fields['amount']['value']['expected'] = expected_tax_amount
            validated_fields['amount']['errors'].append(
                ValidationError(
                    error_level=ValidationErrorLevel.MAJOR,
                    validation_type=ValidationType.BUSINESS,
                    message=f'Tax amount {actual_tax_amount} is not equal to {expected_tax_amount}'
                ).to_dict()
            )
        else:
            validated_fields['amount']['business_validation_status'] = BusinessValidationStatus.MATCH.value
            validated_fields['amount']['value']['expected'] = expected_tax_amount

        if abs(actual_tax_rate - expected_tax_rate) > 0.01:
            validated_fields['rate']['business_validation_status'] = BusinessValidationStatus.MISMATCH.value
            validated_fields['rate']['value']['expected'] = expected_tax_rate
            validated_fields['rate']['errors'].append(
                ValidationError(
                    error_level=ValidationErrorLevel.MAJOR,
                    validation_type=ValidationType.BUSINESS,
                    message=f'Tax rate {actual_tax_rate} is not equal to {expected_tax_rate}'
                ).to_dict()
            )
        else:
            validated_fields['rate']['business_validation_status'] = BusinessValidationStatus.MATCH.value
            validated_fields['rate']['value']['expected'] = expected_tax_rate

        return (actual_tax_amount, expected_tax_amount), validated_fields

    elif is_rate_valid and not is_amount_valid:
        expected_tax_amount = taxable_amount * tax['rate'] / 100

        validated_fields['rate']['business_validation_status'] = BusinessValidationStatus.CANNOT_BE_VALIDATED.value
        validated_fields['amount']['business_validation_status'] = BusinessValidationStatus.DERIVED.value
        validated_fields['amount']['value']['expected'] = expected_tax_amount

        return (None, expected_tax_amount), validated_fields

    elif is_amount_valid and not is_rate_valid:
        expected_tax_rate = taxable_amount * tax['amount'] / 100

        validated_fields['amount']['business_validation_status'] = BusinessValidationStatus.CANNOT_BE_VALIDATED.value
        validated_fields['rate']['business_validation_status'] = BusinessValidationStatus.DERIVED.value
        validated_fields['rate']['value']['expected'] = expected_tax_rate

        return (tax['amount'], None), validated_fields

    else:
        logger.error("Both tax amount and rate are missing.")

        return (None, None), validated_fields


def collect_taxes(
        taxes: List[Dict],
        taxable_amount: Union[int, float]
) -> Tuple[Union[int, float, None], List[Dict[str, Dict]]]:

    tax_amounts: List[Tuple] = []
    taxes_validated_fields: List[Dict[str, Dict]] = []

    for tax in taxes:
        tax_validation_response = tax_validation(tax, taxable_amount)
        tax_amounts.append(tax_validation_response[0])
        taxes_validated_fields.append(tax_validation_response[1])

    total_tax_amount = 0
    for index, tax_amount in enumerate(tax_amounts):
        if tax_amount[0] == tax_amount[1] is None:
            logger.error("Tax fields are missing.")
            return None, taxes_validated_fields

        if tax_amount[1] is None and tax_amount[0] is not None:
            logger.warn("Tax rate was missing but amount present.")
            total_tax_amount += tax_amount[0]
        elif tax_amount[0] is None and tax_amount[1] is not None:
            logger.warn("Tax amount was missing but rate present.")
            total_tax_amount += tax_amount[1]
        else:
            if taxes_validated_fields[index]['amount']['business_validation_status'] == BusinessValidationStatus.MATCH.value:
                total_tax_amount += tax_amount[1]
            else:
                return None, taxes_validated_fields
    return total_tax_amount, taxes_validated_fields


def taxes_validation(
        taxes: List[Dict],
        taxable_amount: Union[int, float],
        total_line_item_amount: Union[int, float]
) -> Tuple[Union[int, float, None], List[Dict[str, Dict]]]:
    total_tax_amount, taxes_validated_fields = collect_taxes(taxes, taxable_amount)

    if total_tax_amount is None:
        return None, taxes_validated_fields

    logger.info(f"The total line item amount is {total_line_item_amount}")
    logger.info(f"The total calculated amount is {taxable_amount + total_tax_amount}")
    if abs(total_line_item_amount - (taxable_amount + total_tax_amount)) <= 0.01 * 100:
        return total_line_item_amount, taxes_validated_fields
    else:
        logger.info("Failed validation.")
        return None, taxes_validated_fields


def line_item_validation(line_item: Dict) -> Tuple[Union[int, float, None], Dict[str, Union[Dict, List]]]:
    from .ValidationConfig import line_item as line_item_config

    line_item_validated_fields: Dict[
        str, Union[Dict, List]] = {}

    # field level validations for line item top level
    for field_name, field_config in line_item_config['fields'].items():
        validated_field = validate_field(line_item, field_name, field_config)
        line_item_validated_fields[field_name] = validated_field.to_dict()

    # field level validations for quantity
    if line_item_validated_fields['quantity']['field_validation_status'] == FieldValidationStatus.VALID.value:
        quantity_validation_response = quantity_validation(line_item['quantity'])
        quantity_value = quantity_validation_response[0]
        line_item_validated_fields['quantity'] = quantity_validation_response[1]
    # if quantity not available or invalid, assume quantity as 1
    else:
        quantity_value = 1

    # if either line item amount or line item rate or the taxes array are invalid or absent then we can go no forward
    is_rate_available = (line_item_validated_fields['rate']['field_validation_status'] ==
                         FieldValidationStatus.VALID.value)
    is_amount_available = (line_item_validated_fields['amount']['field_validation_status'] ==
                           FieldValidationStatus.VALID.value)
    is_taxes_valid = (line_item_validated_fields['taxes']['field_validation_status'] ==
                      FieldValidationStatus.VALID.value)

    line_item_description = line_item['description'] or 'Unknown'

    if not is_rate_available or not is_amount_available or not is_taxes_valid:
        logger.error(f"Line item rate, amount or taxes not available for line item {line_item_description}.")
        return None, line_item_validated_fields

    logger.info(f"Rate and amount are present and valid for line item"
                f"{line_item_validated_fields['description']['value']['actual']}")

    # rate and amount could be the same
    line_item_amount = line_item['amount']
    line_item_rate = line_item['rate']

    if abs(line_item_amount - line_item_rate) <= 0.01 and quantity_value > 1:
        # TODO: figure out what to do when line item rate and amount are the same
        logger.warn(f"Rate and amount are the same for line item "
                    f"{line_item_validated_fields['description']['value']['actual']}")
        return None, line_item_validated_fields

    line_item_price = line_item_rate * quantity_value
    logger.info(f"Validating against line item with rate {line_item_rate} and quantity {quantity_value} for price: {line_item_price}")
    discounted_amount = line_item_price

    is_discount_valid = (
            line_item_validated_fields['discount']['field_validation_status'] == FieldValidationStatus.VALID.value
    )

    need_to_explore_taxes_before_discount = False

    # validate discount
    if is_discount_valid:
        logger.info("Discount object exists and is valid. Validating discount fields now.")
        # discount is present, do business validation
        discount_validation_response_before_tax = discount_validation(line_item['discount'], line_item_price)
        discount_amount_before_tax = discount_validation_response_before_tax[0]
        line_item_validated_fields['discount'] = discount_validation_response_before_tax[1]

        is_discount_amount_not_mismatched = (
                line_item_validated_fields['discount']['amount']['business_validation_status'] !=
                BusinessValidationStatus.MISMATCH.value
        )
        if not is_discount_amount_not_mismatched:
            return None, line_item_validated_fields

        is_discount_amount_derived_or_cannot_be_validated = (
                line_item_validated_fields['discount']['amount']['business_validation_status'] !=
                BusinessValidationStatus.MATCH.value
        )

        if is_discount_amount_derived_or_cannot_be_validated:
            discounted_amount = line_item_price - discount_amount_before_tax[1]
            # will need to explore taxes before discount
            need_to_explore_taxes_before_discount = True
        else:
            discounted_amount = line_item_price - discount_amount_before_tax[0]
            # dont need to explore taxes before discount

    if not need_to_explore_taxes_before_discount:
        logger.info("We do not need to subtract taxes before applying discount.")
        taxes_validation_response = taxes_validation(line_item['taxes'], discounted_amount, line_item_amount)
        line_item_validated_fields['taxes'] = taxes_validation_response[1]
        expected_line_item_amount = taxes_validation_response[0]

        if expected_line_item_amount is None:
            logger.warn("Taxes validation had some error, no total tax returned.")
            line_item_validated_fields['amount']['business_validation_status'] = BusinessValidationStatus.MISMATCH.value
            return None, line_item_validated_fields
        else:
            line_item_validated_fields['amount']['business_validation_status'] = BusinessValidationStatus.MATCH.value
    else:
        logger.info("We may need to subtract taxes before discount.")
        pass

    # do the customer business validations if required
    return line_item_amount, line_item_validated_fields


def invoice_validation(invoice: Dict):
    from .ValidationConfig import invoice as invoice_config

    invoice_validated_fields: Dict[
        str, Union[Dict, List]] = {}

    for field_name, field_config in invoice_config['fields'].items():
        validated_field = validate_field(invoice, field_name, field_config)
        invoice_validated_fields[field_name] = validated_field.to_dict()

    if invoice_validated_fields['customer']['field_validation_status'] == FieldValidationStatus.VALID.value:
        invoice_validated_fields['customer'] = customer_validation(invoice['customer'])

    if invoice_validated_fields['billed_amount']['field_validation_status'] == FieldValidationStatus.VALID.value:
        invoice_validated_fields['billed_amount'] = billed_amount_validation(invoice['billed_amount'])

    if invoice_validated_fields['vendor']['field_validation_status'] == FieldValidationStatus.VALID.value:
        invoice_validated_fields['vendor'] = vendor_validation(invoice['vendor'])

    if invoice_validated_fields['line_items']['field_validation_status'] == FieldValidationStatus.VALID.value:
        line_items_validated_fields: List[
            Dict[str, Union[ValidatedField, Dict[str, ValidatedField], List[Dict[str, ValidatedField]]]]] = []
        for line_item in invoice['line_items']:
            line_item_validation_response = line_item_validation(line_item)
            line_items_validated_fields.append(line_item_validation_response[1])
        invoice_validated_fields['line_items'] = line_items_validated_fields

    # do the customer business validations if required
    return invoice_validated_fields
