from dataclasses import is_dataclass, fields
import PyPDF2
import pandas as pd
import yaml
from typing import Dict, Any, get_origin, get_args, Union, Set, Type

from ..exceptions.BaseValidationError import BaseValidationError
from ..exceptions.MissingRequiredFieldValidationError import MissingRequiredFieldValidationError
from ..exceptions.ValidationErrorType import ValidationErrorType
from ..models.dto.response.v1.ParsedInvoiceResponse import ParsedInvoiceResponseModel
from ..models.entity.InvoiceValidationFailure import InvoiceValidationFailure

from ..logs.logger import setup_logger

logger = setup_logger(__name__)


def load_yaml_file(path: str) -> Dict:
    try:
        with open(path, 'r') as file:
            return yaml.safe_load(file) or {}
    except FileNotFoundError:
        print(f"Config file not found: {path}")
        return {}


def dataclass_to_json_schema(cls) -> dict[str, any]:
    if not is_dataclass(cls):
        raise ValueError("Provided class is not a dataclass.")

    schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    for field in fields(cls):
        field_type = field.type
        field_name = field.name

        if field_type == str:
            field_schema = {"type": "string"}
        elif field_type == int:
            field_schema = {"type": "integer"}
        elif field_type == float:
            field_schema = {"type": "number"}
        elif field_type == bool:
            field_schema = {"type": "boolean"}
        elif field_type == list:
            field_schema = {"type": "array"}
        elif is_dataclass(field_type):
            field_schema = dataclass_to_json_schema(field_type)
        else:
            field_schema = {"type": "string"}  # Default fallback

        schema["properties"][field_name] = field_schema
        schema["required"].append(field_name)

    return schema


def get_annotations(cls):
    annotations = {}
    for field in fields(cls):
        field_type = field.type

        # Check if the type is Optional (i.e., Union with None)
        origin = get_origin(field_type)
        if origin is Union:
            args = get_args(field_type)
            # If v1 of the args is NoneType, it means it's Optional
            if type(None) in args:
                field_type = [arg for arg in args if arg is not type(None)][0]

        # If the field is a nested dataclass, recursively get its annotations
        if hasattr(field_type, "__annotations__"):
            annotations[field.name] = get_annotations(field_type)
        else:
            annotations[field.name] = field_type

    return annotations


from pydantic import BaseModel, ValidationError
from typing import List, Dict


def get_missing_and_empty_keys(
        model: Union[BaseModel, ParsedInvoiceResponseModel],
        data: Dict
) -> List[InvoiceValidationFailure]:
    try:
        print(data)
        ParsedInvoiceResponseModel.model_validate(data)
        return []
    except ValidationError as e:
        validation_errors = []

        for error in e.errors():
            field_path = '.'.join(str(loc) for loc in error['loc'])
            error_type = error['type']
            error_msg = error['msg']
            validation_errors.append(
                InvoiceValidationFailure(
                    field=field_path,
                    failure_type=error_type,
                    message=error_msg
                )
            )

        return sorted(validation_errors, key=lambda x: x.field)


def do_model_validations(
        data: Dict
) -> List[InvoiceValidationFailure]:
    try:
        ParsedInvoiceResponseModel(**data)
        return []
    except ValidationError as e:
        validation_errors = []

        for error in e.errors():
            field_path = '.'.join(str(loc) for loc in error['loc'])
            error_type = error['type']
            error_msg = error['msg']
            validation_errors.append(
                InvoiceValidationFailure(
                    field=field_path,
                    failure_type=error_type,
                    message=error_msg
                )
            )

        return sorted(validation_errors, key=lambda x: x.field)


# TODO: fix this garbage
def find_missing_fields(cls, data: Any, prefix: str = "") -> List[str]:
    data_dict = {}
    if (isinstance(data, dict)):
        data_dict = data

    if (is_dataclass(data)):
        data_dict = data.to_dict()

    missing_fields: list[str] = []
    not_available_strings = ["not available", "N/A", "na", "NA", "n/a", "Not Available", ""]
    schema = get_annotations(cls)
    print(schema)
    if len(prefix) > 0:
        prefix = f"{prefix}."

    for field, value in schema.items():
        print(field)
        if field not in data_dict:
            missing_fields.append(prefix + field)
        else:
            if (
                    data_dict[field] is None or
                    data_dict[field] == [] or data_dict[field] == {} or
                    data_dict[field] in not_available_strings
            ):
                missing_fields.append(prefix + field)
                continue
            # Check nested dataclasses recursively
            if is_dataclass(value):
                print(f"Checking for {field}")
                nested_missing = find_missing_fields(value, data_dict[field], prefix + field)
                for nested_field in nested_missing:
                    missing_fields.append(f"{prefix}{field}.{nested_field}")

            if isinstance(value, dict):
                for k, v in value.items():
                    if k not in data_dict[field]:
                        missing_fields.append(f"{prefix}{field}.{k}")
                    else:
                        if (
                                data_dict[field][k] is None or
                                data_dict[field][k] == [] or data_dict[field][k] == {} or
                                data_dict[field][k] in not_available_strings
                        ):
                            missing_fields.append(f"{prefix}{field}.{k}")
                            continue
                        if is_dataclass(v):
                            nested_missing = find_missing_fields(v, data_dict[field][k], f"{prefix}{field}.{k}")
                            for nested_field in nested_missing:
                                missing_fields.append(f"{prefix}{field}.{k}.{nested_field}")

    return missing_fields


def separate_multi_page_pdf(file_path: str) -> list[str]:
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        pages = []
        for page_num, page in enumerate(reader.pages):
            writer = PyPDF2.PdfWriter()
            writer.add_page(page)

            output_path = f"{file_path}_page_{page_num}.pdf"
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            pages.append(output_path)

    return pages


def is_text_based_pdf_from_bytes(file_bytes):
    reader = PyPDF2.PdfReader(file_bytes)
    text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)

    # Check if we extracted any text
    if any(text):
        return True
    else:
        return False


def is_text_based_pdf(file_path):
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)

        # Check if we extracted any text
        if any(text):
            return True
        else:
            return False


# def convert_class_to_json_schema(cls):
#     invoice_schema = dataclass_to_json_schema(cls)
#     print(json.dumps(invoice_schema, indent=4))

# First, handle the billed_amount taxes
def get_all_tax_categories(data):
    tax_categories = set()

    for invoice in data:
        # Get categories from billed_amount taxes
        if ('invoice' not in invoice) or ('billed_amount' not in invoice['invoice']):
            continue

        if ('taxes' not in invoice['invoice']['billed_amount']):
            continue

        for tax in invoice['invoice']['billed_amount']['taxes']:
            tax_categories.add(tax['tax_category'])

        # Get categories from line_item taxes
        for line_item in invoice['invoice']['line_items']:
            if 'taxes' in line_item:
                for tax in line_item['taxes']:
                    tax_categories.add(tax['tax_category'])

    return list(tax_categories)


def process_taxes(taxes_array, prefix=''):
    if not taxes_array:
        return pd.DataFrame()

    taxes_df = pd.DataFrame(taxes_array)

    # Check which value columns exist
    available_values = []
    for value in ['amount', 'tax_rate']:
        if value in taxes_df.columns:
            available_values.append(value)

    if not available_values:
        return pd.DataFrame()

    taxes_pivot = taxes_df.pivot(
        columns='tax_category',
        values=available_values
    )

    taxes_pivot.columns = [f'{prefix}{col[1].lower()}_{col[0]}' for col in taxes_pivot.columns]
    return taxes_pivot


# def process_taxes(taxes_array, prefix=''):
#     if not taxes_array:
#         return pd.DataFrame()
#     taxes_df = pd.DataFrame(taxes_array)
#     taxes_pivot = taxes_df.pivot(
#         columns='tax_category',
#         values=['amount', 'tax_rate']
#     )
#     taxes_pivot.columns = [f'{prefix}{col[1].lower()}_{col[0]}' for col in taxes_pivot.columns]
#     return taxes_pivot


def process_invoices(data):
    all_rows = []
    tax_categories = get_all_tax_categories(data)

    for invoice_data in data:
        if ('invoice' not in invoice_data) or ('line_items' not in invoice_data['invoice']):
            continue
        # Create main dataframe from line items
        df = pd.json_normalize(
            invoice_data['invoice'],
            record_path='line_items',
            meta=[
                'invoice_number',
                'billed_date',
                'due_date',
                'place_of_supply',
                ['customer', 'name'],
                ['customer', 'billing_address'],
                ['customer', 'shipping_address'],
                ['customer', 'gst_number'],
                ['vendor', 'name'],
                ['vendor', 'address'],
                ['vendor', 'gst_number'],
                ['vendor', 'bank_details', 'bank_name'],
                ['vendor', 'bank_details', 'account_number'],
                ['vendor', 'bank_details', 'branch'],
                ['vendor', 'bank_details', 'branch_address'],
                ['vendor', 'bank_details', 'ifsc'],
                ['billed_amount', 'amount_in_words'],
                ['billed_amount', 'balance_due'],
                ['billed_amount', 'sub_total'],
                ['billed_amount', 'total'],
                ['..', 'file_name']
            ],
            errors='ignore',
            sep='_'
        )

        # Rename line_items columns to add prefix
        line_items_columns = ['amount', 'description', 'hsn_sac', 'quantity', 'rate']
        rename_dict = {col: f'line_items_{col}' for col in line_items_columns}
        df = df.rename(columns=rename_dict)

        # Initialize tax columns
        for category in tax_categories:
            df[f'line_items_{category.lower()}_amount'] = None
            df[f'line_items_{category.lower()}_tax_rate'] = None
            df[f'billed_{category.lower()}_amount'] = None
            df[f'billed_{category.lower()}_tax_rate'] = None

        # Process taxes for each line item row
        for idx in range(len(df)):
            if 'taxes' in invoice_data['invoice']['line_items'][idx]:
                tax_row = process_taxes(invoice_data['invoice']['line_items'][idx]['taxes'], prefix='line_items_')
                for col in tax_row.columns:
                    df.loc[idx, col] = tax_row.iloc[0][col]

        if ('invoice' not in invoice_data) or ('billed_amount' not in invoice_data['invoice']):
            continue

        if ('taxes' not in invoice_data['invoice']['billed_amount']):
            continue

        # Process billed amount taxes
        billed_taxes = process_taxes(
            invoice_data['invoice']['billed_amount']['taxes'],
            prefix='billed_'
        )

        # Add billed taxes to all rows of this invoice
        for col in billed_taxes.columns:
            df[col] = billed_taxes.iloc[0][col]

        # Remove the original taxes column
        df = df.drop('taxes', axis=1, errors='ignore')

        # Add file_path to all rows
        df['file_name'] = invoice_data['file_name']

        all_rows.append(df)

    # Combine all invoices
    final_df = pd.concat(all_rows, ignore_index=True)
    return final_df


def save_as_excel(data, file_name):
    # df = process_invoices(data)
    df = process_invoices([parsed_response.to_dict() for parsed_response in data.values()])
    df.to_csv(file_name, index=False)
