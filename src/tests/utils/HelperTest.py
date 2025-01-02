import pytest

from ...app.models.dto.response.v1.ParsedInvoiceResponse import ParsedInvoiceResponse
from ...app.models.entity.templates.v1.BankDetails import BankDetails
from ...app.models.entity.templates.v1.BilledAmount import BilledAmount
from ...app.models.entity.templates.v1.Customer import Customer
from ...app.models.entity.templates.v1.Vendor import Vendor
from ...app.utils.Helper import find_missing_fields


# Your dataclasses here (Tax, LineItem, etc...)

class TestInvoiceValidation:
    @pytest.fixture
    def complete_invoice_data(self):
        return {
            "billed_amount": {
                "amount_in_words": "Eight Thousand Eight Hundred Fifty Only",
                "balance_due": 22420,
                "sub_total": 7500,
                "taxes": [
                    {
                        "amount": 675,
                        "tax_category": "CGST",
                        "tax_rate": 9
                    },
                    {
                        "amount": 675,
                        "tax_category": "SGST",
                        "tax_rate": 9
                    }
                ],
                "total": 8850
            },
            "billed_date": "01-Jul-2024",
            "customer": {
                "billing_address": "F-27, Regency Farms, Asola...",
                "gst_number": "07AEGFS0831M1ZU",
                "name": "Solidum And Stars Guild LLP",
                "shipping_address": "F-27, Regency Farms, Asola..."
            },
            "due_date": "16-Jul-2024",
            "invoice_number": "23241595",
            "line_items": [
                {
                    "amount": 7500,
                    "description": "100 Mbps @ 2500.00...",
                    "hsn_sac": 998422,
                    "quantity": 1,
                    "rate": 2500,
                    "taxes": [
                        {
                            "amount": 675,
                            "tax_category": "CGST",
                            "tax_rate": 9
                        },
                        {
                            "amount": 675,
                            "tax_category": "SGST",
                            "tax_rate": 9
                        }
                    ]
                }
            ],
            "place_of_supply": "New Delhi",
            "vendor": {
                "address": "Khasra No:429 Main Road Satbari...",
                "bank_details": {
                    "account_number": "50200007416172",
                    "bank_name": "HDFC",
                    "branch": "MEHRAULI",
                    "branch_address": "Some Address",
                    "ifsc": "HDFC0001671"
                },
                "gst_number": "07ERFPS5614J1ZE",
                "name": "LINE INTERNET"
            }
        }

    def test_complete_invoice_has_no_missing_fields(self, complete_invoice_data):
        """Test that a complete invoice has no missing fields"""
        missing_fields = find_missing_fields(ParsedInvoiceResponse, complete_invoice_data)
        assert len(missing_fields) == 0, f"Expected no missing fields but found: {missing_fields}"

    def test_empty_strings_are_considered_missing(self):
        """Test that empty strings are considered missing fields"""
        data = {
            "billed_amount": {
                "amount_in_words": "",  # Empty string
                "balance_due": 100,
                "sub_total": 100,
                "total": 100,
                "taxes": [{"amount": 10, "tax_category": "CGST", "tax_rate": 10}]
            }
        }
        missing_fields = find_missing_fields(BilledAmount, data["billed_amount"])
        assert "amount_in_words" in missing_fields

    def test_none_values_are_considered_missing(self):
        """Test that None values are considered missing fields"""
        data = {
            "customer": {
                "billing_address": None,
                "gst_number": "TEST123",
                "name": "Test Company",
                "shipping_address": "Test Address"
            }
        }
        missing_fields = find_missing_fields(Customer, data["customer"])
        assert "billing_address" in missing_fields

    def test_empty_lists_are_considered_missing(self):
        """Test that empty lists are considered missing fields"""
        data = {
            "line_items": []
        }
        missing_fields = find_missing_fields(ParsedInvoiceResponse, data)
        assert "line_items" in missing_fields

    def test_empty_nested_objects_are_considered_missing(self):
        """Test that empty nested objects are considered missing"""
        data = {
            "vendor": {}
        }
        missing_fields = find_missing_fields(ParsedInvoiceResponse, data)
        assert "vendor" in missing_fields

    def test_nested_field_path_is_correct(self):
        """Test that nested field paths are correctly formatted"""
        data = Vendor(
            bank_details=BankDetails(
                account_number="",
                bank_name="HDFC",
                branch="MEHRAULI",
                branch_address="",
                ifsc_code="HDFC0001671"
            )
        )
        missing_fields = find_missing_fields(Vendor, data)
        print(missing_fields)
        assert "bank_details.account_number" in missing_fields

    def test_not_available_strings_are_considered_missing(self):
        """Test that 'N/A' and similar strings are considered missing"""
        data = {
            "billed_date": "N/A",
            "due_date": "not available",
            "invoice_number": "NA"
        }
        missing_fields = find_missing_fields(ParsedInvoiceResponse, data)
        assert all(field in missing_fields for field in ["billed_date", "due_date", "invoice_number"])

    @pytest.mark.parametrize("na_string", [
        "not available", "N/A", "na", "NA", "n/a", "Not Available", ""
    ])
    def test_various_na_string_formats(self, na_string):
        """Test different formats of N/A strings are all considered missing"""
        data = {
            "invoice_number": na_string
        }
        missing_fields = find_missing_fields(ParsedInvoiceResponse, data)
        assert "invoice_number" in missing_fields
