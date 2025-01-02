
GST_REGEX = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[0-9]{1}[A-Z]{2}$'
PAN_REGEX = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
GST_RANGE = (15, 15)
PAN_RANGE = (10, 10)
IFSC_REGEX = r'^[A-Z]{4}0[A-Z0-9]{6}$'
IFSC_RANGE = (11, 11)

invoice = {
    "fields": {
        "invoice_number": {
            "type": str,
            "range": (4, None),
            "pattern": None,
            "business": None,
            "required": True
        },
        "due_date": {
            "type": str,
            "range": (4, None),
            "pattern": None,
            "business": None,
            "required": False
        },
        "billing_date": {
            "type": str,
            "range": (4, None),
            "pattern": None,
            "business": None,
            "required": False
        },
        "currency_code": {
            "type": str,
            "range": (2, None),
            "pattern": None,
            "business": None,
            "required": False
        },
        "place_of_supply": {
            "type": str,
            "range": (2, None),
            "pattern": None,
            "business": None,
            "required": False
        },
        "line_items": {
            "type": list,
            "range": (1, None),
            "pattern": None,
            "business": None,
            "required": True
        },
        "customer": {
            "type": dict,
            "range": None,
            "pattern": None,
            "business": None,
            "required": True
        },
        "vendor": {
            "type": dict,
            "range": None,
            "pattern": None,
            "business": None,
            "required": True
        },
        "billed_amount": {
            "type": dict,
            "range": None,
            "pattern": None,
            "business": None,
            "required": True
        }
    }
}
line_item = {
    "fields": {
        "amount": {
            "type": (int, float),
            "range": (0, None),
            "pattern": None,
            "business": None,
            "required": True
        },
        "rate": {
            "type": (int, float),
            "range": (0, None),
            "pattern": None,
            "business": None,
            "required": True
        },
        "description": {
            "type": str,
            "range": (4, None),
            "pattern": None,
            "business": None,
            "required": True
        },
        "hsn_sac": {
            "type": str,
            "range": (4, None),
            "pattern": None,
            "business": None,
            "required": True
        },
        "quantity": {
            "type": dict,
            "range": None,
            "pattern": None,
            "business": None,
            "required": True
        },
        "discount": {
            "type": dict,
            "range": None,
            "pattern": None,
            "business": None,
            "required": False
        },
        "taxes": {
            "type": list,
            "range": (1, None),
            "pattern": None,
            "business": None,
            "required": True
        }
    }
}
tax = {
    "fields": {
        "amount": {
            "type": (int, float),
            "range": (0, None),
            "pattern": None,
            "business": None,
            "required": True
        },
        "category": {
            "type": str,
            "range": (4, None),
            "pattern": None,
            "business": None,
            "required": True
        },
        "rate": {
            "type": (int, float),
            "range": (0, 100),
            "pattern": None,
            "business": None,
            "required": True
        }
    }
}
discount = {
    "fields": {
        "amount": {
            "type": (int, float),
            "range": (0, None),
            "pattern": None,
            "business": None,
            "required": False
        },
        "percentage": {
            "type": (int, float),
            "range": (0, 100),
            "pattern": None,
            "business": None,
            "required": False
        }
    }
}
quantity = {
    "fields": {
        "value": {
            "type": (int, float),
            "range": (0, None),
            "pattern": None,
            "business": None,
            "required": False
        },
        "unit": {
            "type": str,
            "range": (1, None),
            "pattern": None,
            "business": None,
            "required": False
        }
    }
}
billed_amount = {
    "fields": {
        "amount_in_words": {
            "type": str,
            "range": (4, None),
            "pattern": None,
            "business": None,
            "required": False
        },
        "balance_due": {
            "type": (int, float),
            "range": (0, None),
            "pattern": None,
            "business": None,
            "required": True
        },
        "previous_dues": {
            "type": (int, float),
            "range": (0, None),
            "pattern": None,
            "business": None,
            "required": False
        },
        "sub_total": {
            "type": (int, float),
            "range": (0, None),
            "pattern": None,
            "business": None,
            "required": False
        },
        "total": {
            "type": (int, float),
            "range": (0, None),
            "pattern": None,
            "business": None,
            "required": True
        }
    }
}
bank_details = {
    "fields": {
        "account_number": {
            "type": str,
            "range": (9, 17),
            "pattern": None,
            "business": None,
            "required": True
        },
        "ifsc": {
            "type": str,
            "range": IFSC_RANGE,
            "pattern": IFSC_REGEX,
            "business": None,
            "required": True
        },
        "name": {
            "type": str,
            "range": (4, None),
            "pattern": None,
            "business": None,
            "required": True
        },
        "branch": {
            "type": str,
            "range": (4, None),
            "pattern": None,
            "business": None,
            "required": False
        },
        "bank_name": {
            "type": str,
            "range": (4, None),
            "pattern": None,
            "business": None,
            "required": True
        },
        "branch_address": {
            "type": str,
            "range": (4, None),
            "pattern": None,
            "business": None,
            "required": False
        }
    }
}
vendor = {
    "fields": {
        "address": {
            "type": str,
            "range": (4, None),
            "pattern": None,
            "business": None,
            "required": True
        },
        "gst_number": {
            "type": str,
            "range": GST_RANGE,
            "pattern": GST_REGEX,
            "business": None,
            "required": True
        },
        "name": {
            "type": str,
            "range": (4, None),
            "pattern": None,
            "business": None,
            "required": True
        },
        "pan": {
            "type": str,
            "range": PAN_RANGE,
            "pattern": PAN_REGEX,
            "business": None,
            "required": False
        },
        "upi_id": {
            "type": str,
            "range": (4, None),
            "pattern": None,
            "business": None,
            "required": False
        },
        "bank_details": {
            "type": dict,
            "range": None,
            "pattern": None,
            "business": None,
            "required": True
        }
    }
}
customer = {
    "fields": {
        "billing_address": {
            "type": str,
            "range": (4, None),
            "pattern": None,
            "business": None,
            "required": True
        },
        "gst_number": {
            "type": str,
            "range": GST_RANGE,
            "pattern": GST_REGEX,
            "business": None,
            "required": True
        },
        "name": {
            "type": str,
            "range": (4, None),
            "pattern": None,
            "business": None,
            "required": True
        },
        "pan": {
            "type": str,
            "range": PAN_RANGE,
            "pattern": PAN_REGEX,
            "business": None,
            "required": True
        },
        "shipping_address": {
            "type": str,
            "range": (4, None),
            "pattern": None,
            "business": None,
            "required": False
        }
    }
}
