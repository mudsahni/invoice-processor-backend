import io

from flask import Flask
from werkzeug.datastructures import FileStorage

from .StorageService import StorageService
from ..config.Configuration import Configuration
from ..models.entity.PDFTypeFlags import PDFTypeFlags
from ..models.enum.PDFType import PDFType
from ..logs.logger import setup_logger
from ..models.entity.Invoice import Invoice
from ..services.anthropic.AnthropicClient import AnthropicClient
from ..services.openai.OpenAIClient import OpenAIClient
from typing import Dict, List

import PyPDF2


class ParserService:
    ALLOWED_EXTENSIONS = {'pdf'}

    def __init__(self, app: Flask):
        self.app = app
        self.config: Configuration = app.config['CONFIGURATION']
        self.openai_client: OpenAIClient = OpenAIClient(api_key=self.config.open_ai_api_key)
        self.anthropic_client: AnthropicClient = AnthropicClient(api_key=self.config.anthropic_api_key)
        self.logger = setup_logger(__name__)
        self.UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
        self.PROCESSED_FOLDER = app.config['PROCESSED_FOLDER']
        self.storage_service = StorageService(app.config['CONFIGURATION'].bucket_name)

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ParserService.ALLOWED_EXTENSIONS

    def parse(self, job_id: str, file_paths: List[FileStorage]) -> Dict[str, Invoice]:
        raise NotImplementedError("Method not implemented")

    @classmethod
    def is_text_based_and_not_multi_page(cls, file: bytes) -> List[PDFType]:
        res: List[PDFType] = []
        pdf_file: io.BytesIO = io.BytesIO(file)

        # reader: Optional[PdfReader] = None
        # with open(f"./{file_path}", "rb") as file:
        reader = PyPDF2.PdfReader(pdf_file)

        text = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)

        # Check if we extracted any text
        if any(text):
            res.append(PDFType.TEXT)
        else:
            res.append(PDFType.IMAGE)

        if len(reader.pages) == 1:
            res.append(PDFType.SINGLE_PAGE)
        else:
            res.append(PDFType.MULTI_PAGE)

        return res

    @classmethod
    def flag_pdf_types(cls, file: Dict) -> PDFTypeFlags:
        pdf_types: List[PDFType] = ParserService.is_text_based_and_not_multi_page(file['file_content'])
        is_multi_page = PDFType.MULTI_PAGE in pdf_types
        is_image_based = PDFType.IMAGE in pdf_types

        return PDFTypeFlags(
            file_name=file['file_path'],
            file_content=file['file_content'],
            is_multi_page=is_multi_page,
            is_image_based=is_image_based
        )
