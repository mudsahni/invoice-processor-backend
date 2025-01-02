from typing import Dict


class AIClient:

    def __init__(self, api_key: str):
        self.api_key = api_key

    def process_pdf(self, model: str, file_path: str, file_content: bytes, prompt: str) -> Dict:
        raise NotImplementedError("Method not implemented")
