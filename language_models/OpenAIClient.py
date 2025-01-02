import json
from typing import Literal

from openai import OpenAI
from openai.types.beta.threads.message_create_params import (
    Attachment,
    AttachmentToolFileSearch,
)

from language_models.LanguageModelAPI import LanguageModelAPI
from src.app.logs.logger import setup_logger
from models.Invoice import Invoice


class OpenAIClient(LanguageModelAPI):
    DEFAULT_MODEL = "gpt-4o-mini-2024-07-18"
    RUN_STATUSES = Literal["queued", "in_progress", "requires_action", "cancelling", "cancelled", "failed", "completed", "incomplete", "expired"]

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.logger = setup_logger(__name__)
        self.client = OpenAI(api_key=api_key)
        self.pdf_assistant = None
        self._initialize_pdf_assistant()

    def _initialize_pdf_assistant(self):
        self.logger.info("Initializing PDF assistant")
        self.pdf_assistant = self.client.beta.assistants.create(
            model=self.DEFAULT_MODEL,
            description="An assistant to extract the contents of PDF files.",
            tools=[{"type": "file_search"}],
            name="PDF assistant",
        )

    def parse_pdfs_to_dicts(self, file_paths: list[str], prompt: str) -> dict[str, dict[str, any]]:
        results: dict[str, dict[str, any]] = {}
        batch_size = 3

        for i in range(0, len(file_paths), batch_size):
            batch_files = file_paths[i:i + batch_size]
            self.logger.info(f"Processing batch {i // batch_size + 1} with {len(batch_files)} files")
            threads = {file_path: self.client.beta.threads.create() for file_path in batch_files}
            pdf_files = {
                file_path: self.client.files.create(file=open(file_path, "rb"), purpose="assistants")
                for file_path in batch_files
            }

            for file_path, thread in threads.items():
                self.logger.info(f"Processing PDF[{file_path}]")
                self.client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    attachments=[
                        Attachment(
                            file_id=pdf_files[file_path].id, tools=[AttachmentToolFileSearch(type="file_search")]
                        )
                    ],
                    content=prompt,
                )

            runs = {
                file_path: self.client.beta.threads.runs.create_and_poll(
                    thread_id=thread.id, assistant_id=self.pdf_assistant.id, timeout=1000
                ) for file_path, thread in threads.items()
            }

            for file_path, run in runs.items():
                if run.status != "completed":
                    raise Exception(f"Run failed for file[{file_path}]:", run.status)

            for file_path, thread in threads.items():
                messages_cursor = self.client.beta.threads.messages.list(thread_id=thread.id)
                messages = [message for message in messages_cursor]
                res_txt = messages[0].content[0].text.value.replace("```json", "").replace("```", "")
                results[file_path] = json.loads(res_txt)

        return results

    def parse_pdf_to_dict(self, file_path: str, prompt: str) -> dict[str, any]:
        # create thread
        thread = self.client.beta.threads.create()
        # upload file
        pdf_file = self.client.files.create(file=open(file_path, "rb"), purpose="assistants")

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

        # create run
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=self.pdf_assistant.id,
            timeout=1000,
            tools=[],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": Invoice.__name__.lower(),
                    "schema": Invoice.model_json_schema(),
                    "strict": True
                }
            }
        )

        if run.status != "completed":
            raise Exception("Run failed:", run.status)

        messages_cursor = self.client.beta.threads.messages.list(thread_id=thread.id)
        messages = [message for message in messages_cursor]

        print(messages[0].content[0].text.value)
        # Output text
        res_txt = messages[0].content[0].text.value.replace("```json", "").replace("```", "")
        print(res_txt)
        return json.loads(res_txt)
