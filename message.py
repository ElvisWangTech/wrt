from enum import Enum

class SN_TYPE(Enum):
    processing = 1
    finished = 2
    error = 3
    dataGenerated = 4
    keyInfo = 5

class SN:
    def __init__(self, text, type: SN_TYPE) -> None:
        self.text = text
        self.type = type

    def __str__(self) -> str:
        return "text: {}, type: {}".format(self.text, self.type)
