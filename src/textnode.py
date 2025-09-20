from enum import Enum

class TextType(Enum):
    PLAIN_TEXT = 0
    BOLD_TEXT = 1
    ITALIC_TEXT = 2
    CODE_TEXT = 3
    LINK_ANCHOR_TEXT_URL = 4
    IMAGE_ALT_TEXT_URL = 5

class BlockType(Enum):
    PARAGRAPH = 0
    HEADING = 1
    CODE = 2
    QUOTE = 3
    UNORDERED_LIST = 4
    ORDERED_LIST = 5

class TextNode():
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        if self.text == other.text and self.text_type == other.text_type and self.url == other.url:
            return True
        else:
            return False

    def __repr__(self):
        return f'TextNode({self.text}, {self.text_type}, {self.url})'


