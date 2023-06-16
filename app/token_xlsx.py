from openpyxl.cell import Cell


# Перенести в отдельный модуль
def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]


class SupportMerge:
    start_column: int
    start_row: int
    end_column: int
    end_row: int

    def __init__(self):
        self.start_column = -1
        self.start_row = -1
        self.end_row = -1
        self.end_column = -1


class MyStyle:
    font: any
    alignment: any

    def __init__(self):
        self.font = None
        self.alignment = None


class TokenTypeXlsx:
    token_name: str
    text_cell: str
    cell: Cell
    merge: any
    num_row: int
    my_style: MyStyle

    def __init__(self):
        self.token_name = ""
        self.text_cell = ""
        self.merge = None
        self.my_style = MyStyle()


class TokenTypeCollection:
    parent: any
    main_token: str
    sub_tokens: dict

    def __init__(self):
        self.parent = None
        self.main_token = ''
        self.sub_tokens = {}


class TokenXlsx:
    tokens_str = {}
    tokens_collection = {}

    def __init__(self):
        self.tokens_str = {}
        self.tokens_collection = {}

    def add_token_str(self, cell: Cell):
        temp_token = TokenTypeXlsx()
        temp_token.cell = cell
        temp_token.my_style.font = cell.font
        temp_token.my_style.alignment = cell.alignment
        clear_token = cell.internal_value.translate({ord(i): None for i in '{}'})
        temp_token.token_name = cell.internal_value
        self.tokens_str.update({clear_token: temp_token})

    def cell_is_merge(self, cell: Cell):
        ranges = cell.parent.merged_cells.ranges
        coord = cell.coordinate
        for range in ranges:
            if coord in range.coord:
                support_merge = SupportMerge()
                support_merge.start_row = range.min_row
                support_merge.start_column = range.min_col
                support_merge.end_row = range.max_row
                support_merge.end_column = range.max_col
                return support_merge
        return None

    def add_token_type_collection(self, main_token: str, full_name: str, cell: Cell, parent=None):
        clear_token = main_token.translate({ord(i): None for i in '{}'})
        clear_token_list = clear_token.split('.')
        if parent is not None:
            parent_token: TokenTypeCollection = parent.sub_tokens.get(clear_token_list[0])
        else:
            parent_token: TokenTypeCollection = self.tokens_collection.get(clear_token_list[0])
        if parent_token is not None:
            if len(clear_token_list) == 2:
                sub_token = TokenTypeXlsx()
                sub_token.token_name = full_name
                sub_token.cell = cell
                sub_token.my_style.font = cell.font
                sub_token.my_style.alignment = cell.alignment
                sub_token.text_cell = cell.value
                sub_token.num_row = cell.row
                sub_token.merge = self.cell_is_merge(cell)
                parent_token.sub_tokens.update({clear_token_list[1]: sub_token})
            else:
                delete_str = clear_token_list[0] + '.'
                clear_token = remove_prefix(clear_token, delete_str)
                self.add_token_type_collection(clear_token, full_name, cell, parent_token)
        else:
            temp_token = TokenTypeCollection()
            temp_token.main_token = clear_token_list[0]
            sub_token = TokenTypeXlsx()
            sub_token.token_name = full_name
            sub_token.cell = cell
            sub_token.my_style.font = cell.font
            sub_token.my_style.alignment = cell.alignment
            sub_token.text_cell = cell.value
            sub_token.num_row = cell.row
            sub_token.merge = self.cell_is_merge(cell)
            temp_token.sub_tokens.update({clear_token_list[1]: sub_token})
            if parent is not None:
                parent.sub_tokens.update({clear_token_list[0]: temp_token})
            else:
                self.tokens_collection.update({clear_token_list[0]: temp_token})
