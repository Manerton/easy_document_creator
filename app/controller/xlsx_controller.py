import os

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
    for file in files:
        if file.filename == '':
            flash('Нет выбранного файла')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if 'xlsx' in filename:
                doc.open_document(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                doc.start()

