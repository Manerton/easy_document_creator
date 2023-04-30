import json
import os

from datetime import date

from flask import request, flash, redirect
from werkzeug.utils import secure_filename

from app.xlsx_analyzer import XlsxAnalyzer
from app.main import app



ALLOWED_EXTENSIONS = {'xlsx', 'json'}

def allowed_file(filename):
    """ Функция проверки расширения файла """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/api/generate/file-xlsx", methods=['POST'])
def init_file_xlsx():
    if 'file' not in request.files:
        flash('Не читаемый файл')
        return redirect(request.url)
    files = request.files.getlist("file")
    doc = XlsxAnalyzer()
    save_file = "NotName"
    for file in files:
        if file.filename == '':
            flash('Нет выбранного файла')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if 'xlsx' in filename:
                save_file = str(date.today()) + filename
                doc.open_document(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                doc.start_search()
            elif 'json' in filename:
                with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), encoding="utf8") as read_file:
                    data = json.load(read_file)
                    read_file.close()
                doc.init_data(data)
    doc.start_replace()
    doc.save_document(os.path.join(app.config['UPLOAD_FOLDER'], save_file))
    return "ok"
    # doc.save_file(os.path.join(app.config['UPLOAD_FOLDER'], save_file))
    # return redirect(url_for('download_file', name=save_file))
