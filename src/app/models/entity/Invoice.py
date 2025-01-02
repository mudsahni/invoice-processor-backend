from dataclasses import dataclass
from datetime import datetime

from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any

from ...constants.Defaults import DEFAULT_CREATED_BY
from ...models.dto.response.v1.ParsedInvoiceResponse import ParsedInvoiceResponse
from ...models.entity.templates.ClientDetails import ClientDetails
from ...models.enum.ParsingStatus import ParsingStatus
from ...models.enum.Tenant import Tenant
from ...validations.Validation import invoice_validation


def from_parsed_invoice_response(
        job_id: str,
        parsed_invoice_response: ParsedInvoiceResponse,
        tenant: Tenant,
        file_name: str,
        is_multi_page: bool,
        is_image: bool,
        retry: bool,
        client_details: ClientDetails,
        status: ParsingStatus,
        created_by: str = DEFAULT_CREATED_BY
):
    validation_response = invoice_validation(parsed_invoice_response.to_dict())
    return Invoice(
        job_id=job_id,
        tenant=tenant,
        file_name=file_name,
        is_multi_page=is_multi_page,
        is_image=is_image,
        retry=retry,
        status=status,
        created_date=datetime.now().isoformat(),
        created_by=created_by,
        updated_date=None,
        updated_by=None,
        validation=validation_response,
        client_details=client_details,
        invoice=parsed_invoice_response,

    )

@dataclass_json
@dataclass
class Invoice:
    job_id: str
    file_name: str
    is_multi_page: bool
    is_image: bool
    retry: bool
    tenant: Tenant
    status: ParsingStatus
    validation: Dict
    created_date: str
    updated_date: str
    created_by: str
    updated_by: str
    client_details: ClientDetails
    error: Optional[str] = None
    invoice: Optional[ParsedInvoiceResponse] = None

    def to_dict(self):
        return self.__dict__
