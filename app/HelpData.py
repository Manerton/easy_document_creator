from enum import Enum
from docx.text.paragraph import Paragraph


class TokenTypeString:
    paragraph: Paragraph
    old_text_paragraph: str
    main_token: str

    def __init__(self):
        self.paragraph = None
        self.old_text_paragraph = ''
        self.main_token = ''


class SupportTable:
    table: any
    last_row: any
    old_row: any

    def __init__(self):
        self.table = None
        self.last_row = None
        self.old_row = None


class TokenTypeCollection:
    parent: any
    main_token: str
    sub_tokens: dict
    table: SupportTable

    def __init__(self):
        self.parent = None
        self.main_token = ''
        self.sub_tokens = {}
        self.table = SupportTable()


def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]


class SimpleParagraphData:
    text: str
    runs: any
    sub_tokens = []


class Tokens:
    TokensTypeString = {}
    TokensTypeCollection = {}
    TokensTypeList = {}

    def add_token_type_list(self, main_token, paragraph):
        temp_token = TokenTypeString()
        temp_token.paragraph = paragraph
        temp_token.main_token = main_token
        clear_token = main_token.translate({ord(i): None for i in '{}'})
        self.TokensTypeString.update({clear_token: temp_token})

    def add_token_type_string(self, main_token, paragraph):
        temp_token = TokenTypeString()
        temp_token.paragraph = paragraph
        temp_token.main_token = main_token
        clear_token = main_token.translate({ord(i): None for i in '{}'})
        self.TokensTypeString.update({clear_token: temp_token})

    def add_token_type_collection(self, main_token, full_name, paragraph, table=None, parent=None):
        clear_token = main_token.translate({ord(i): None for i in '{}'})
        clear_token_list = clear_token.split('.')
        if parent is not None:
            parent_token: TokenTypeCollection = parent.sub_tokens.get(clear_token_list[0])
        else:
            parent_token: TokenTypeCollection = self.TokensTypeCollection.get(clear_token_list[0])
        if parent_token is not None:
            if len(clear_token_list) == 2:
                sub_token = TokenTypeString()
                sub_token.main_token = full_name
                sub_token.old_text_paragraph = paragraph.text
                sub_token.paragraph = paragraph
                parent_token.sub_tokens.update({clear_token_list[1]: sub_token})
            else:
                delete_str = clear_token_list[0] + "."
                clear_token = remove_prefix(clear_token, delete_str)
                self.add_token_type_collection(clear_token, full_name, paragraph, None, parent_token)
        else:
            temp_token = TokenTypeCollection()
            temp_token.table = table
            temp_token.main_token = clear_token_list[0]
            sub_token = TokenTypeString()
            sub_token.old_text_paragraph = paragraph.text
            sub_token.main_token = full_name
            sub_token.paragraph = paragraph
            temp_token.sub_tokens.update({clear_token_list[1]: sub_token})
            if parent is not None:
                parent.sub_tokens.update({clear_token_list[0]: temp_token})
            else:
                self.TokensTypeCollection.update({clear_token_list[0]: temp_token})
