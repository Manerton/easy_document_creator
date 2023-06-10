import mimetypes
import uuid

from flask_login import login_required

from app.controller.xlsx_controller import delete_file_from_temp
from app.database.api_key_repository import check_api_key
from app.main import app
from flask import request, flash, redirect, url_for, render_template, Blueprint, make_response, Response
from app.docx_analyzer import DocxAnalyzer
from werkzeug.utils import secure_filename
from app.models.ResponseModel import ResponseModel, ErrorResponseModel
import os
import json

from app.database.process_repository import (
    get_process_by_id,
    put_file,
    get_file,
    delete_file
)

from app.database.file_repository import ( insert_my_file )
from app.models.my_file import MyFile

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


# Генерация документа сиюминутным способом со стороны стороннего сервиса через api
@docx.route("/api/generate/now/file-docx/", methods=['POST'])
async def api_now_file_docx():
    api_key = request.headers["authorization"]
    if api_key is None or not await check_api_key(api_key):
        return ErrorResponseModel("Error api-key", 400, "Invalid api-key")
    if not request.files.get('file', None):
        return ErrorResponseModel("Error data", 400, "Files not Found")
    # Генерация имени для готового документа
    result_filename = str(uuid.uuid4()) + '.docx'
    # Объявление имени для шаблонного файла
    template_filename = str(uuid.uuid4()) + '.docx'
    # Объявление имени для файла с данными
    json_data_filename = str(uuid.uuid4()) + '.json'
    files = request.files.getlist("file")
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if filename.endswith('.docx'):
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], template_filename))
            elif filename.endswith('.json'):
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], json_data_filename))
        else:
            return ErrorResponseModel('Error data', 400, 'Invalid file type')
    await docx_worker(json_data_filename, template_filename, result_filename)
    # Открытие сохранённого готового файла
    save_file = open(os.path.join(app.config['UPLOAD_FOLDER'], result_filename), 'rb')
    file = save_file.read()
    save_file.close()
    await delete_template_file(json_data_filename, template_filename, result_filename)

    response = make_response(file)
    _type = mimetypes.guess_type(result_filename)
    response.mimetype = _type[0]
    return response


# Генерация документа отложенным способом со стороны стороннего сервиса через api
@docx.route("/api/generate/file-docx/<process_id>", methods=['POST'])
async def api_file_docx(process_id):
    api_key = request.headers["authorization"]
    if api_key is None or not await check_api_key(api_key):
        return ErrorResponseModel("Error api-key", 400, "Invalid api-key")
    if request.files.get('file', None):
        json_file = request.files['file']
        if not json_file.filename.endswith('.json'):
            return ErrorResponseModel("Error data", 400, "Invalid file type")
        file_id = await start_create_docx_with_process(process_id, json_file)

        response = Response()
        response.status_code = 202
        response.location = request.host_url + url_for('process.download_result_file_api', file_id=file_id)
        return response
    return ErrorResponseModel("Error data", 400, "File not Found")


# Генерация документа со стороны web-приложения
@docx.route("/generate/file-docx/<process_id>", methods=['POST'])
@login_required
async def file_docx(process_id):
    if request.files.get('file', None):
        json_file = request.files['file']
        await start_create_docx_with_process(process_id, json_file)
    return redirect(url_for('process.open_process', id=process_id))


# Начало запуска процесса создания документа
async def start_create_docx_with_process(process_id, json_file):
    process = get_process_by_id(process_id)
    template_file_id = process['file_id']
    template_file_byte = get_file(template_file_id)
    # Генерация временного имени шаблонного файла
    template_filename = str(uuid.uuid4()) + '.docx'
    # Генерация временного имена готового файла
    result_filename = str(uuid.uuid4()) + '.docx'
    # Генерация временног имени для файла с данными
    json_data_filename = str(uuid.uuid4()) + '.json'
    # Временная загрузка шаблонного файла на пк
    output = open(os.path.join(app.config['UPLOAD_FOLDER'], template_filename), 'wb')
    output.write(template_file_byte)
    output.close()
    # Временная загрузка json данных на пк
    json_file.save(os.path.join(app.config['UPLOAD_FOLDER'], json_data_filename))
    # Запуск генерации документа
    await docx_worker(json_data_filename, template_filename, result_filename)
    # Сохранение готового документа в БД
    file_id = await save_result_file_in_db(result_filename, process_id)
    # Удаление ранее созданных файлов
    await delete_template_file(json_data_filename, template_filename, result_filename)
    return file_id


# async def upload_start_file_in_directory(files):
#
#     for file in files:
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             if 'docx' in filename:
#                 doc.open_document(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#                 doc.start_search_tokens()
#             elif 'json' in filename:
#                 with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), encoding="utf8") as read_file:
#                     data = json.load(read_file)
#                     read_file.close()
#                 doc.init_data(data)


# Создание документа из docx
async def docx_worker(json_filename: str, template_filename: str, result_filename: str):
    # Чтение json файла из временного хранилища
    with open(os.path.join(app.config['UPLOAD_FOLDER'], json_filename), encoding="utf8") as read_file:
        data = json.load(read_file)
        read_file.close()
    # Создание объекта класса обработки docx файлов
    document = DocxAnalyzer()
    # Инициализация шаблона как документа
    document.open_document(os.path.join(app.config['UPLOAD_FOLDER'], template_filename))
    # Инициализация данных из json
    document.init_data(data)
    # Поиск токенов
    document.start_search_tokens()
    # Замена токенов
    document.start_replace()
    # Сохранение готового файла
    document.save_file(os.path.join(app.config['UPLOAD_FOLDER'], result_filename))


# Загружаем файл в базу
async def save_result_file_in_db(result_filename, process_id):
    save_file = open(os.path.join(app.config['UPLOAD_FOLDER'], result_filename), 'rb')
    file = save_file.read()
    file_id = put_file(file, result_filename)
    save_file.close()
    my_file = MyFile(result_filename, file_id, process_id)
    insert_my_file(my_file)

    return file_id


# Удаление ранее созданных файлов из папки для временных файлов
async def delete_template_file(json_filename: str, template_filename: str, result_filename: str):
    # Удаляем json с данными
    delete_file_from_temp(os.path.join(app.config['UPLOAD_FOLDER'], json_filename))
    # Удаляем шаблон документа
    delete_file_from_temp(os.path.join(app.config['UPLOAD_FOLDER'], template_filename))
    # Удаляем готовый полученный документ
    delete_file_from_temp(os.path.join(app.config['UPLOAD_FOLDER'], result_filename))
