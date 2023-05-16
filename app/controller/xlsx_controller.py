import json
import os
import mimetypes
from datetime import date
from io import StringIO

from flask import request, flash, redirect, url_for, Blueprint, make_response
from werkzeug.utils import secure_filename

from app.xlsx_analyzer import XlsxAnalyzer
from app.main import app

from app.database.process_repository import (
    get_processes,
    get_process_by_id,
    insert_process,
    update_process,
    delete_process,
    put_file,
    get_file, get_file_database,
    delete_file
)


xlsx = Blueprint('xlsx', __name__)

ALLOWED_EXTENSIONS = {'xlsx', 'json'}


def allowed_file(filename):
    """ Функция проверки расширения файла """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# @xlsx.route("/api/generate/file-xlsx", methods=['POST'])
# def init_file_xlsx():
#     if 'file' not in request.files:
#         flash('Не читаемый файл')
#         return redirect(request.url)
#     files = request.files.getlist("file")
#     doc = XlsxAnalyzer()
#     save_file = "NotName"
#     for file in files:
#         if file.filename == '':
#             flash('Нет выбранного файла')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             if 'xlsx' in filename:
#                 save_file = str(date.today()) + filename
#                 doc.open_document(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#                 doc.start_search()
#             elif 'json' in filename:
#                 with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), encoding="utf8") as read_file:
#                     data = json.load(read_file)
#                     read_file.close()
#                 doc.init_data(data)
#     doc.start_replace()
#     doc.save_document(os.path.join(app.config['UPLOAD_FOLDER'], save_file))
#     return redirect(url_for('download_file', name=save_file))

@xlsx.route("/api/generate/file-xlsx/<process_id>", methods=['POST'])
def file_xlsx(process_id):
    head = request.headers
    if request.files.get('file', None):
        json_file = request.files['file']
        process = get_process_by_id(process_id)
        template_file_byte = get_file(process['file_id'])

        output = open('C:/Users/assba/PycharmProjects/easy_document_creator/temp_down/' + 'test.xlsx', "wb")
        output.write(template_file_byte)
        output = open('C:/Users/assba/PycharmProjects/easy_document_creator/temp_down/' + json_file.filename, "wb")
        output.write(json_file)

        document = XlsxAnalyzer()
        # data = json.load(json_file)
        document.open_document('C:/Users/assba/PycharmProjects/easy_document_creator/temp_down/' + 'test.xlsx')
        document.init_data(json.load('C:/Users/assba/PycharmProjects/easy_document_creator/temp_down/' + json_file.filename))
        document.start_search()
        document.start_replace()
        document.save_document('test')

    pass






@xlsx.route("/api/generate/file-xlsx", methods=['POST'])
def init_file_xlsx():


    if 'file' not in request.files:
        flash('Не читаемый файл')
        return redirect(request.url)
    files = request.files.getlist("file")
    for file in files:
        if file.filename == '':
            flash('Нет выбранного файла')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if 'xlsx' in filename:
                # output = open('C:/Users/assba/PycharmProjects/easy_document_creator/temp_down/' + filename, "wb")
                # output.write(ret_file)
                file_id = put_file(file)
                strrr = str(file_id)
                ret_file = get_file(strrr)
                response = make_response(ret_file)
                _type = mimetypes.guess_type(file.filename)
                response.mimetype = _type[0]
                return response
    # return redirect(url_for('download_file', name=save_file))
