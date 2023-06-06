import json
import os
import mimetypes
import uuid

from flask import request, flash, redirect, url_for, Blueprint, make_response
from werkzeug.utils import secure_filename

from app.models.my_file import MyFile
from app.xlsx_analyzer import XlsxAnalyzer
from app.main import app

from app.database.process_repository import (
    get_process_by_id,
    put_file,
    get_file,
    delete_file
)

from app.database.file_repository import ( insert_my_file )


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
        template_file_id = process['file_id']
        template_file_byte = get_file(template_file_id)
        # Генерация временного имени файла шаблона
        temp_random_filename = str(process_id) + '.xlsx'
        result_filename = str(uuid.uuid4()) + '.xlsx'
        # Временная загрузка шаблонного файла на пк
        output = open(os.path.join(app.config['UPLOAD_FOLDER'], temp_random_filename), 'wb')
        output.write(template_file_byte)
        # Временная загрузка json данных на пк
        json_file.save(os.path.join(app.config['UPLOAD_FOLDER'], json_file.filename))
        # Чтение json файла из временного хранилища
        with open(os.path.join(app.config['UPLOAD_FOLDER'], json_file.filename), encoding="utf8") as read_file:
            data = json.load(read_file)
            read_file.close()
        # Создание объекта класса обработки xlsx файлов
        document = XlsxAnalyzer()
        # Инициализация шаблона как документа
        document.open_document(os.path.join(app.config['UPLOAD_FOLDER'], temp_random_filename))
        # Инициализация данных из json
        document.init_data(data)
        # Поиск токенов
        document.start_search()
        # Замена токенов
        document.start_replace()
        # Сохранение готового файла
        document.save_document(os.path.join(app.config['UPLOAD_FOLDER'], result_filename))
        # Открытие сохранеённого готового файла
        save_file = open(os.path.join(app.config['UPLOAD_FOLDER'], result_filename), 'rb')
        file = save_file.read()
        # Загружаем файл в базу
        file_id = put_file(file, result_filename)
        # Удаление ранее созданных файлов из папки для временных файлов
        # delete_file_from_temp(os.path.join(app.config['UPLOAD_FOLDER'], result_filename))
        # delete_file_from_temp(os.path.join(app.config['UPLOAD_FOLDER'], temp_random_filename))
        # delete_file_from_temp(os.path.join(app.config['UPLOAD_FOLDER'], json_file.filename))
        myFile = MyFile(result_filename, file_id, process_id)
        insert_my_file(myFile)
        return redirect(url_for('process.open_process', id=process_id))


def delete_file_from_temp(path: str):
    if os.path.isfile(path):
        os.remove(path)


# @xlsx.route("/api/generate/file-xlsx", methods=['POST'])
# def init_file_xlsx():
#     if 'file' not in request.files:
#         flash('Не читаемый файл')
#         return redirect(request.url)
#     files = request.files.getlist("file")
#     for file in files:
#         if file.filename == '':
#             flash('Нет выбранного файла')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             if 'xlsx' in filename:
#                 # output = open('C:/Users/assba/PycharmProjects/easy_document_creator/temp_down/' + filename, "wb")
#                 # output.write(ret_file)
#                 file_id = put_file(file)
#                 strrr = str(file_id)
#                 ret_file = get_file(strrr)
#                 response = make_response(ret_file)
#                 _type = mimetypes.guess_type(file.filename)
#                 response.mimetype = _type[0]
#                 return response
#     # return redirect(url_for('download_file', name=save_file))
