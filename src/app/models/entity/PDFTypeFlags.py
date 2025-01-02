from dataclasses import dataclass


@dataclass
class PDFTypeFlags:

    file_name: str
    file_content: bytes
    is_image_based: bool
    is_multi_page: bool
