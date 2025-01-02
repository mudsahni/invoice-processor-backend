

class LanguageModelAPI:

    def __init__(self, api_key: str):
        self.api_key: str = api_key

    def process_pdf(self, file_path: str, prompt: str) -> dict:
        pass