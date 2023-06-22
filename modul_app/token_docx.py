import re

from docx.text.font import Font
from docx.text.paragraph import Paragraph



class SupportTable:
    table: any
    row: any
    old_cells: any

    def __init__(self):
        self.table = None
        self.row = None
        self.old_cells = None


class TokenTypeString:
    paragraph: Paragraph
    format: any
    old_text_paragraph: str
    font: any
    main_token: str

    def __init__(self):
        self.paragraph = None
        self.old_text_paragraph = ''
        self.font = None
        self.main_token = ''


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


def get_clear_token(text: str):
    return re.search('{{(.+?)}}', text).group(1)


def get_font_and_size(runs, word):
    for run in runs:
        if word in run.text or run.text in word:
            return run.font


def set_font_and_size(runs, word: str, font: Font):
    if font is None:
        return
    for run in runs:
        if word in run.text:
            run.font.all_caps = font.all_caps
            run.font.bold = font.bold
            run.font.color.rgb = font.color.rgb
            run.font.color.theme_color = font.color.theme_color
            run.font.complex_script = font.complex_script
            run.font.cs_bold = font.cs_bold
            run.font.cs_italic = font.cs_italic
            run.font.double_strike = font.double_strike
            run.font.emboss = font.emboss
            run.font.hidden = font.hidden
            run.font.highlight_color = font.highlight_color
            run.font.imprint = font.imprint
            run.font.italic = font.italic
            run.font.math = font.math
            run.font.name = font.name
            run.font.no_proof = font.no_proof
            run.font.outline = font.outline
            run.font.shadow = font.shadow
            run.font.size = font.size
            run.font.small_caps = font.small_caps
            run.font.spec_vanish = font.spec_vanish
            run.font.strike = font.strike
            run.font.subscript = font.subscript
            run.font.superscript = font.superscript
            run.font.underline = font.underline
            run.font.web_hidden = font.web_hidden


class Tokens:
    TokensTypeString = {}
    TokensTypeCollection = {}
    TokensTypeList = {}

    def __init__(self):
        self.TokensTypeString = {}
        self.TokensTypeCollection = {}
        self.TokensTypeList = {}

    def add_token_type_list(self, main_token, paragraph):
        temp_token = TokenTypeString()
        temp_token.paragraph = paragraph
        temp_token.format = paragraph.paragraph_format
        temp_token.main_token = main_token
        clear_token = main_token.translate({ord(i): None for i in '{}'})
        font = get_font_and_size(paragraph.runs, clear_token)
        temp_token.font = font
        self.TokensTypeString.update({clear_token: temp_token})

    def add_token_type_string(self, main_token, paragraph):
        temp_token = TokenTypeString()
        temp_token.paragraph = paragraph
        temp_token.main_token = main_token
        clear_token = main_token.translate({ord(i): None for i in '{}'})
        font = get_font_and_size(paragraph.runs, clear_token)
        temp_token.font = font
        self.TokensTypeString.update({clear_token: temp_token})

    def add_token_type_collection(self, main_token, full_name, paragraph: Paragraph, table: SupportTable=None, parent=None):
        clear_token = main_token.translate({ord(i): None for i in '{}'})
        font = get_font_and_size(paragraph.runs, clear_token)
        clear_token_list = clear_token.split('.')
        if parent is not None:
            parent_token: TokenTypeCollection = parent.sub_tokens.get(clear_token_list[0])
        else:
            parent_token: TokenTypeCollection = self.TokensTypeCollection.get(clear_token_list[0])
        if parent_token is not None:
            if len(clear_token_list) == 2:
                sub_token = TokenTypeString()
                sub_token.main_token = full_name
                sub_token.font = font
                sub_token.old_text_paragraph = paragraph.text
                sub_token.paragraph = paragraph
                sub_token.format = paragraph.paragraph_format
                parent_token.sub_tokens.update({clear_token_list[1]: sub_token})
            else:
                delete_str = clear_token_list[0] + "."
                clear_token = remove_prefix(clear_token, delete_str)
                self.add_token_type_collection(clear_token, full_name, paragraph, table, parent_token)
        else:
            temp_token = TokenTypeCollection()
            temp_token.table = table
            temp_token.main_token = clear_token_list[0]
            if parent is not None:
                temp_token.parent = parent
                parent.sub_tokens.update({clear_token_list[0]: temp_token})
            else:
                self.TokensTypeCollection.update({clear_token_list[0]: temp_token})
            if len(clear_token_list) == 2:
                sub_token = TokenTypeString()
                sub_token.font = font
                sub_token.old_text_paragraph = paragraph.text
                sub_token.main_token = full_name
                sub_token.paragraph = paragraph
                sub_token.format = paragraph.paragraph_format
                temp_token.sub_tokens.update({clear_token_list[1]: sub_token})
                if parent is not None:
                    temp_token.parent = parent
                    parent.sub_tokens.update({clear_token_list[0]: temp_token})
                else:
                    self.TokensTypeCollection.update({clear_token_list[0]: temp_token})
            else:
                delete_str = clear_token_list[0] + "."
                clear_token = remove_prefix(clear_token, delete_str)
                self.add_token_type_collection(clear_token, full_name, paragraph, table, temp_token)
