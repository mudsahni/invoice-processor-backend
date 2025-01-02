import io
from typing import Dict

import certifi
import httpx
from openai import OpenAI
from openai.types.beta import Assistant
from openai.types.beta.threads.message import Attachment
from openai.types.beta.threads.message_create_params import AttachmentToolFileSearch

from ...exceptions.OpenAIException import OpenAIException
from ...logs.logger import setup_logger
from ...models.enum.OpenAIRunStatus import OpenAIRunStatus
from ...services.AIClient import AIClient
import json

# Configure httpx client with SSL verification
httpx_client = httpx.Client(
    verify=False,
    trust_env=True
)

class OpenAIClient(AIClient):

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.logger = setup_logger(__name__)
        self.client = OpenAI(api_key=api_key, http_client=httpx_client)
        self.assistants: Dict[str, Assistant] = {}

    def _initialize_pdf_assistant(
            self,
            model: str,
    ):
        self.logger.info("Initializing PDF assistant")
        self.assistants[model] = self.client.beta.assistants.create(
            model=model,
            description="An assistant to extract the contents of PDF files.",
            instructions="You are expert at structured data extraction. When given a PDF for an invoice and/or bill, "
                         "you will extract the relevant data from it and convert it to the given json structure.",
            tools=[{"type": "file_search"}],
            name="Invoice Parsing Assistant"
        )

    def process_pdf(
            self,
            model: str,
            file_path: str,
            file_content: bytes,
            prompt: str,
    ) -> Dict:
        # create or fetch assistant
        if model not in self.assistants:
            self._initialize_pdf_assistant(model)

        PDF_ASSISTANT = self.assistants[model]

        # create thread
        thread = self.client.beta.threads.create()
        # upload file
        pdf_file = self.client.files.create(file=io.BytesIO(file_content), purpose="assistants")

        # create message
        message = self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            attachments=[
                Attachment(
                    file_id=pdf_file.id, tools=[AttachmentToolFileSearch(type="file_search")]
                )
            ],
            content=prompt,
        )

        # create run and poll it
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=PDF_ASSISTANT.id,
            timeout=1000,
        )

        # if run is not completed successfully
        if run.status != OpenAIRunStatus.COMPLETED.value:
            raise OpenAIException(f"Run failed: {run.status}, {run.metadata}, {run.to_json()}")

        # fetch generated messages
        messages_cursor = self.client.beta.threads.messages.list(thread_id=thread.id)
        messages = [message for message in messages_cursor]

        # Output text
        return json.loads(OpenAIClient.remove_json_tags(messages[0].content[0].text.value))

    @classmethod
    def remove_json_tags(cls, text: str) -> str:
        return text.replace("```json", "").replace("```", "")