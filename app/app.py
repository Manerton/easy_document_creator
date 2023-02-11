from flask import Flask
from newDocxAnalyzer import newDocxAnalyzer
from docxtpl import DocxTemplate
import json

app = Flask(__name__)
doc = newDocxAnalyzer()

contextJson = {
    "name": [
        {
            "first": "name1",
            "second": "name2",
        },
        {
            "first": "name1",
            "second": "name2",
        }
    ],
    "date": "02.01.2024",
}

context = {
    "list": ["list1", "list2", "list3"],
    "name": ["name1", "name2", "name3"],
    "date": "02.01.2002",
    "test": ["test1", "test2"]
}


@app.route("/")
def list_token():
    doc.open_document("test1.docx")
    doc.start_search_tokens()
    return "success"

@app.route("/2")
def replace_token():
    with open("data.json", encoding="utf8") as read_file:
        data = json.load(read_file)
        read_file.close()
    doc.init_data(data)
    doc.start_replace()
    doc.save_file("new_file.docx")
    return 'success'


if __name__ == '__main__':
    app.run()