from enum import Enum

class Color(Enum):
    red = 1
    green = 2
    blue = 3

    @classmethod
    def from_name(cls, text: str):
        text = text.lower()
        for enum_item in iter(cls):
            if enum_item.name == text:
                return enum_item
        # -- OOPS:
        raise ValueError("UNEXPECTED: {}".format(text))
