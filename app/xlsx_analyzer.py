from openpyxl import workbook, load_workbook
from openpyxl.cell import Cell
from token_xlsx import TokenXlsx

class XlsxAnalyzer:
    document: workbook
    tokens_xlsx: TokenXlsx

    def open_document(self, name_doc: str):
        self.document = load_workbook(name_doc)
        self.tokens_xlsx = TokenXlsx()

    def start(self):
        worksheets = self.document.worksheets
        for worksheet in worksheets:
            for row in worksheet.iter_rows():
                for cell in row:
                    self.search_token(cell)

    def search_token(self, cell: Cell):
        cell_text = cell.value
        if cell_text is None:
            return
        if "{{" and "}}" in cell_text:
            self.tokens_xlsx.add_token(cell)

    def get_token(self):
        return self.tokens_xlsx.tokens

    def save_document(self, new_name: str):
        self.document.save(new_name)
