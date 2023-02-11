from enum import Enum
from docx.text.paragraph import Paragraph


class TokenTypeString:
    paragraph: Paragraph
    main_token: str


class TokenTypeList:
    paragraph: Paragraph
    main_token: str


class TokenTypeCollection:
    parent: any
    main_token: str
    sub_tokens = []
    is_table = False


def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]


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

    def add_token_type_collection(self, main_token, paragraph, is_table=False, parent=None):
        clear_token = main_token.translate({ord(i): None for i in '{}'})
        clear_token_list = clear_token.split('.')
        parent_token: TokenTypeCollection = self.TokensTypeCollection.get(clear_token_list[0])
        if parent_token is not None:
            if len(clear_token_list) == 2:
                sub_token = TokenTypeString()
                sub_token.main_token = clear_token_list[1]
                sub_token.paragraph = paragraph
                parent_token.sub_tokens.append(sub_token)
            else:
                delete_str = clear_token_list[0] + "."
                clear_token = remove_prefix(clear_token, delete_str)
                self.add_token_type_collection(clear_token, paragraph, is_table, parent_token)
        else:
            temp_token = TokenTypeCollection()
            temp_token.parent = parent
            temp_token.is_table = is_table
            temp_token.main_token = clear_token_list[0]
            sub_token = TokenTypeString()
            sub_token.main_token = clear_token_list[1]
            sub_token.paragraph = paragraph
            temp_token.sub_tokens.append(sub_token)
            self.TokensTypeCollection.update({clear_token_list[0]: temp_token})

