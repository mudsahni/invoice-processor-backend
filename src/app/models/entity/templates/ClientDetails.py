from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class ClientDetails:
    client: str
    model: str

    def to_dict(self):
        return self.__dict__
