import anthropic
from anthropic.types.beta.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.beta.messages.batch_create_params import Request
from ContentType import ContentType
from AnthropicModel import AnthropicModel

class AnthropicAPI(object):

    ANTHROPIC_BETA_PDF_API_HEADER = "pdfs-2024-09-25"
    ANTHROPIC_BETA_BATCH_API_HEADER = "message-batches-2024-09-24"
    ANTHROPIC_BETA_HEADER_KEY = "anthropic-beta"

    def __init__(self, api_key: str):
        self.api_key: str = api_key
        self.in_progress_batches = []
        self.processed_batches = []
        self.client = anthropic.Anthropic(api_key=api_key)
        # self.logger = logging.getLogger("AnthropicAPI")

    def process_pdf_parsing_batch_request(self, requests: list[Request]):
        batch_request = self.send_batch_request(
            headers={
                AnthropicAPI.ANTHROPIC_BETA_HEADER_KEY: AnthropicAPI.ANTHROPIC_BETA_BATCH_API_HEADER,
                AnthropicAPI.ANTHROPIC_BETA_HEADER_KEY: AnthropicAPI.ANTHROPIC_BETA_PDF_API_HEADER
            },
            requests=requests
        )
        # self.logger.info(f"Batch with request id {batch_request['id']} has been created.")
        self.in_progress_batches.append(batch_request)

    def send_batch_request(self, headers: dict, requests: list[Request]):
        return self.client.beta.messages.batches.create(
            extra_headers=headers,
            requests=requests
        )

    @classmethod
    def add_requests_to_batch(cls, requests: list[Request]):
        batch_requests: list[Request] = []
        for request in requests:
            batch_requests.append(request)
        return batch_requests

    @classmethod
    def create_pdf_parsing_request(cls,
                                   request_id: str,
                                   data: str,
                                   message_text: str,
                                   request_prefix: str = "invoice_parser_request_"
                                   ) -> Request:
        return AnthropicAPI.create_request(
            request_id=request_id,
            content_type=ContentType.DOCUMENT,
            source_type="base64",
            media_type="application/pdf",
            data=data,
            message_text=message_text,
            request_prefix=request_prefix
        )

    @classmethod
    def create_request(
            cls,
            request_id: str,
            content_type: ContentType,
            source_type: str,
            media_type: str,
            data,
            message_text: str,
            model: AnthropicModel = AnthropicModel.SONNET_3_5,
            max_tokens: int = 1024,
            role: str = "user",
            request_prefix: str = "invoice_parser_request_"
    ) -> Request:
        return Request(
                custom_id=f"{request_prefix}-{request_id}",
                params=MessageCreateParamsNonStreaming(
                    model=model.value,
                    max_tokens=max_tokens,
                    messages=[{
                        "role": role,
                        "content": [
                            {
                                "type": content_type.value,
                                "source": {
                                    "type": source_type,
                                    "media_type": media_type,
                                    "data": data
                                }
                            },
                            {
                                "type": "text",
                                "text": message_text

                            }
                        ]
                    }]
                )
            )

