import base64
import io
import json

import anthropic
import httpx
from anthropic import Anthropic
from typing import List, Dict, Optional
from ...logs.logger import setup_logger
from ...models.dto.request.AnthropicAPIRequest import build_anthropic_api_pdf_parsing_request
from ...services.AIClient import AIClient

# Configure httpx client with SSL verification
httpx_client = httpx.Client(
    verify=False,
    trust_env=True
)
class AnthropicClient(AIClient):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.logger = setup_logger(__name__)
        self.client: Anthropic = anthropic.Anthropic(api_key=api_key, http_client=httpx_client)
        self.MAX_TOKENS = 8192
        self.ANTHROPIC_PDF_HEADER_KEY = "anthropic-beta"
        self.ANTHROPIC_PDF_HEADER_VALUE = "pdfs-2024-09-25"

    def process_pdf(self, model: str, file_path: str, file_content: bytes, prompt: str) -> Dict:
        base64_pdf: Optional[str] = None
        # with open(f"./{file_path}", "rb") as f:
        #     base64_pdf = base64.b64encode(f.read()).decode()

        base64_pdf = base64.b64encode(file_content).decode()

        if base64_pdf is None:
            # TODO: Change to specific exception
            raise Exception("Could not read PDF file")

        messages: List[Dict] = [build_anthropic_api_pdf_parsing_request(base64_pdf, prompt)]
        response = self.client.messages.create(
            model=model,
            messages=messages,
            max_tokens=self.MAX_TOKENS,
            extra_headers={self.ANTHROPIC_PDF_HEADER_KEY: self.ANTHROPIC_PDF_HEADER_VALUE}
        )

        try:
            invoice_response = response.content[0].to_dict()['text']
            if invoice_response is None:
                self.logger.error("Error parsing PDF with path: " + file_path)
                return {}
            data = json.loads(invoice_response)
            self.logger.info("Successfully parsed PDF with path: " + file_path)
            return data
        except Exception as e:
            self.logger.error("Error parsing PDF with path: " + file_path)
            return {}

