from openpyxl.cell import Cell


class TokenTypeXlsx:
    token_name: str
    cell: Cell
    is_merge: bool

    def __init__(self):
        self.token_name = ""
        self.is_merge = False


class TokenXlsx:
    tokens = {}

    def add_token(self, cell: Cell):
        temp_token = TokenTypeXlsx()
        temp_token.cell = cell
        temp_token.token_name = cell.internal_value
        self.tokens.update({cell.internal_value: temp_token})



