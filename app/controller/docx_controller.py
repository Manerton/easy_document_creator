from app.main import app
from flask import request, flash, redirect, url_for, render_template, Blueprint
from app.docx_analyzer import DocxAnalyzer
from werkzeug.utils import secure_filename
import os
import json


docx = Blueprint('docx', __name__)


ALLOWED_EXTENSIONS = {'docx', 'json'}


def allowed_file(filename):
    """ Функция проверки расширения файла """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@docx.route("/api/generate/file-docx", methods=['POST'])
def init_file_docx():
    if not request.files.get('file', None):
        flash('Файл не выбран')
        return redirect(request.url)
    files = request.files.getlist("file")
    save_file = 'NotName'
    doc = DocxAnalyzer()
    for file in files:
        if file.filename == '':
            flash('Нет выбранного файла')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if 'docx' in filename:
                doc.open_document(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                doc.start_search_tokens()
                save_file = 'new2' + filename
            elif 'json' in filename:
                with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), encoding="utf8") as read_file:
                    data = json.load(read_file)
                    read_file.close()
                doc.init_data(data)
    doc.start_replace()
    doc.save_file(os.path.join(app.config['UPLOAD_FOLDER'], save_file))
    return redirect(url_for('download_file', name=save_file))

