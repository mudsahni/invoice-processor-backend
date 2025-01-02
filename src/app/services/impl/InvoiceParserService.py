from typing import IO, Union

from flask import Flask
from werkzeug.datastructures import FileStorage

from ...exceptions.OpenAIException import OpenAIException
from ...models.entity.PDFTypeFlags import PDFTypeFlags
from ...constants.Defaults import DEFAULT_CREATED_BY
from ...db.Firestore import Firestore
from ...models.dto.response.v1.ParsedInvoiceResponse import ParsedInvoiceResponse
from ...models.entity.templates.ClientDetails import ClientDetails
from ...models.entity.Invoice import Invoice, from_parsed_invoice_response
from ...models.enum.AIClient import AIClient
from ...models.enum.ParsingStatus import ParsingStatus
from ...models.enum.Tenant import Tenant
from ...services.ParserService import ParserService
import json
from typing import Dict, List


class InvoiceParserService(ParserService):
    # TODO: To be removed
    DEFAULT_TENANT = Tenant.PERFECT_ACCOUNTING_AND_SHARED_SERVICES
    DEFAULT_OPENAI_MODEL = "gpt-4o-mini-2024-07-18"
    # DEFAULT_OPENAI_MODEL = "gpt-4o"
    DEFAULT_ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"

    # DEFAULT_ANTHROPIC_MODEL = "claude-3-5-haiku-20241022"

    def __init__(self, app: Flask):
        super().__init__(app)
        self.template: dict = {}
        self.multi_page_template: dict = {}
        self.DEFAULT_INVOICE_PROMPT_TEMPLATE_PATH = "./resources/prompt_templates/invoice_template.json"
        self.MULTI_PAGE_INVOICE_PROMPT_TEMPLATE_PATH = "./resources/prompt_templates/multi_page_invoice_template.json"
        self.firestore = Firestore(self.config.env, self.config.tenant_id)
        # Open the JSON file
        with open(self.DEFAULT_INVOICE_PROMPT_TEMPLATE_PATH, 'r') as file:
            # Load the JSON data into a Python dictionary
            self.template = json.load(file)

        with open(self.MULTI_PAGE_INVOICE_PROMPT_TEMPLATE_PATH, 'r') as file:
            # Load the JSON data into a Python dictionary
            self.multi_page_template = json.load(file)
        self.multi_page_template = self.template

    def _save_invoice(
            self,
            job_id: str,
            is_multi_page: bool,
            is_image: bool,
            retry: bool,
            client_details: ClientDetails,
            parsed_invoice_dict: Dict,
            file_path: str) -> Invoice:

        """
        Converts the parsed invoice response to an Invoice entity object and saves it to Firestore.

        Missing and error fields are identified and saved in the Invoice entity object as well,
        along with metadata.

        Parameters:
        job_id (str): Unique UUID for the job run from the UI
        is_multi_page (bool): Boolean value if PDF has multiple pages
        is_image (bool): Boolean value if PDF is an image
        parsed_invoice_dict (dict): Dictionary object returned from the OpenAI API
        file_path (str): Path to the invoice file

        Returns:
        Invoice: The Invoice entity object saved to Firestore.
        """
        # Converting the parsed invoice dict to a ParsedInvoiceResponse object
        parsed_invoice_response = ParsedInvoiceResponse(**parsed_invoice_dict['invoice'])
        # Converting the ParsedInvoiceResponse object to an Invoice object
        # TODO: Should pass request executor name as created by
        invoice = from_parsed_invoice_response(
            job_id,
            parsed_invoice_response,
            self.DEFAULT_TENANT.value,
            file_path,
            is_multi_page,
            is_image,
            retry,
            client_details,
            ParsingStatus.SUCCESS.value,
            DEFAULT_CREATED_BY
        )
        # Saving the invoice to Firestore
        # TODO: Should be saved in the invoices collection for an org, eg "expedia/invoices"
        document_id = self.firestore.add_document(f"tenants/{self.DEFAULT_TENANT.value}/invoices", invoice.to_dict())
        self.logger.info("Document ID: " + document_id)
        return invoice

    def _get_files_with_parsing_flags(self, file_paths: list[str]) -> List[PDFTypeFlags]:
        files_with_flags: List[PDFTypeFlags] = []
        for file_path in file_paths:
            blob = self.storage_service.bucket.blob(file_path)
            content: bytes = blob.download_as_bytes()
            file_obj = {
                "file_path": file_path,
                "file_content": content
            }
            files_with_flags.append(ParserService.flag_pdf_types(file_obj))
        return files_with_flags

    def _get_parsed_invoices(self, job_id: str, file_paths: list[str]) -> Dict[str, Invoice]:
        parsed_invoices: Dict[str, Invoice] = {}

        files_with_pdf_types: List[PDFTypeFlags] = self._get_files_with_parsing_flags(file_paths)
        failed_files: List[PDFTypeFlags] = []

        for file_with_flags in files_with_pdf_types:
            if file_with_flags.is_multi_page or file_with_flags.is_image_based:
                client = AIClient.ANTHROPIC.value
                model_function = self.anthropic_client.process_pdf
                model = self.DEFAULT_ANTHROPIC_MODEL
                template = self.multi_page_template
            else:
                client = AIClient.OPENAI.value
                model_function = self.openai_client.process_pdf
                model = self.DEFAULT_OPENAI_MODEL
                template = self.template

            try:
                parsed_invoice: Dict = model_function(
                    model,
                    file_with_flags.file_name,
                    file_with_flags.file_content,
                    template["prompt"] + "\n" + json.dumps(template["template"])
                )
                if len(parsed_invoice) == 0 or 'invoice' not in parsed_invoice:
                    self.logger.error("Error parsing PDF with path: " + file_with_flags.file_name)
                    continue
                parsed_invoices[file_with_flags.file_name] = self._save_invoice(
                    job_id,
                    file_with_flags.is_multi_page,
                    file_with_flags.is_image_based,
                    False,
                    ClientDetails(client, model),
                    parsed_invoice,
                    file_with_flags.file_name
                )
            except OpenAIException as e:
                failed_files.append(file_with_flags)
                self.logger.error("Error parsing PDF with path: " + file_with_flags.file_name + " Error: " + str(e))

        for file_with_flags in failed_files:
            parsed_invoice: Dict = self.anthropic_client.process_pdf(
                self.DEFAULT_ANTHROPIC_MODEL,
                file_with_flags.file_name,
                file_with_flags.file_content,
                self.template["prompt"] + "\n" +
                json.dumps(self.template["template"])
            )
            if len(parsed_invoice) == 0 or 'invoice' not in parsed_invoice:
                self.logger.error("Error parsing PDF with path: " + file_with_flags.file_name)
                continue
            parsed_invoices[file_with_flags.file_name] = self._save_invoice(
                job_id,
                file_with_flags.is_multi_page,
                file_with_flags.is_image_based,
                True,
                ClientDetails(AIClient.ANTHROPIC.value, self.DEFAULT_ANTHROPIC_MODEL),
                parsed_invoice,
                file_with_flags.file_name
            )

        return parsed_invoices

    def parse(self, job_id: str, files: List[FileStorage]) -> Dict[str, Invoice]:
        processing_results: Dict[str, Invoice] = {}
        upload_paths: list[str] = []

        for file in files:
            if file and self.allowed_file(file.filename):
                try:
                    # Upload files to GCS
                    upload_paths.extend(self.storage_service.upload_files(job_id, [file]))
                except Exception as e:
                    processing_results[file.filename] = Invoice(
                        file_name=file.filename,
                        status='error',
                        error=str(e),
                        created_by=DEFAULT_CREATED_BY,
                        tenant=self.DEFAULT_TENANT,
                        invoice=None
                    )
            else:
                processing_results[file.filename] = Invoice(
                    file_name=file.filename,
                    status='error',
                    error="Invalid file type",
                    created_by=DEFAULT_CREATED_BY,
                    tenant=self.DEFAULT_TENANT,
                    invoice=None
                )

        processing_results = {**self._get_parsed_invoices(job_id, upload_paths)}

        return processing_results

    def _decide_model(self, content: Union[str, IO]):
        """If more than v1 page or image pdf, then use claude"""
        pass
