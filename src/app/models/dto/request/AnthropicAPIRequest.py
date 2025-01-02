from typing import Dict, List, Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass
@dataclass_json
class Source:
    type: str
    media_type: str
    data: str

    def __init__(self, type: str, media_type: str, data: str):
        self.type = type
        self.media_type = media_type
        self.data = data

    def to_dict(self):
        return self.__dict__


@dataclass
@dataclass_json
class Content:
    type: str
    source: Optional[Source]
    text: Optional[str]

    def __init__(self, type: str, source: Source | None, text: str | None):
        self.type = type
        self.source = source
        self.text = text

    def to_dict(self):
        return self.__dict__


@dataclass_json
@dataclass
class AnthropicAPIRequest:
    role: str
    content: List[Content]

    def __init__(self, role: str, content: List[Content]):
        self.role = role
        self.content = content

    def to_dict(self):
        return self.__dict__


def build_anthropic_api_pdf_parsing_request(
        pdf: str,
        prompt: str
) -> Dict:
    return {
        "role": "user",
        "content": [
            {
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": pdf
                }
            },
            {
                "type": "text",
                "text": prompt
            }
        ]
    }
    # return AnthropicAPIRequest(
    #     role="user",
    #     content=[
    #         Content(
    #             type="document",
    #             source=Source(
    #                 type="base64",
    #                 media_type="application/pdf",
    #                 data=pdf
    #             ),
    #             text=None
    #         ),
    #         Content(
    #             type="text",
    #             text=prompt,
    #             source=None
    #         )
    #     ]
    # )
