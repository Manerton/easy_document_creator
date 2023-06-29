import mimetypes
import uuid

from flask_login import login_required

from modul_app.database.api_key_repository import check_api_key
from modul_app.main import app
from flask import request, flash, redirect, url_for, render_template, Blueprint, make_response, Response
from modul_app.docx_analyzer import DocxAnalyzer
from werkzeug.utils import secure_filename
from modul_app.models.ResponseModel import ResponseModel, ErrorResponseModel
import os
import json

from modul_app.database.process_repository import (
    get_process_by_id,
    put_file,
    get_file,
    delete_file
)

from modul_app.database.file_repository import (insert_my_file, delete_template_file, save_result_file_in_db)
from modul_app.models.my_file import MyFile

docx = Blueprint('docx', __name__)
ALLOWED_EXTENSIONS = {'docx', 'json'}


def allowed_file(filename):
    """ Функция проверки расширения файла """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Генерация документа сиюминутным способом со стороны стороннего сервиса через api
@docx.route("/api/generate/now/file-docx/", methods=['POST'])
async def api_now_file_docx():
    api_key = request.headers.environ.get('HTTP_AUTHORIZATION')
    if api_key is None or not await check_api_key(api_key):
        return ErrorResponseModel("Error api-key", 400, "Invalid api-key")
    if not request.files.get('file', None):
        return ErrorResponseModel("Error data", 400, "Files not Found")
    list_filenames = await create_filenames_for_docx()
    files = request.files.getlist("file")
    if len(files) != 2:
        return ErrorResponseModel('Error count Files', 400, 'The number of files must be equal to 2')
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if filename.endswith('.docx'):
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], list_filenames[0]))
            elif filename.endswith('.json'):
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], list_filenames[1]))
        else:
            return ErrorResponseModel('Error data', 400, 'Invalid file type')
    await docx_worker(list_filenames[0], list_filenames[1], list_filenames[2])
    # Открытие сохранённого готового файла
    save_file = open(os.path.join(app.config['UPLOAD_FOLDER'], list_filenames[2]), 'rb')
    file = save_file.read()
    save_file.close()
    await delete_template_file(list_filenames[0], list_filenames[1], list_filenames[2])
    # Подготовка ответа
    response = make_response(file)
    _type = mimetypes.guess_type(list_filenames[2])
    response.mimetype = _type[0]
    return response


@docx.route("/api/generate/now/file-docx/<process_id>", methods=['POST'])
async def api_now_file_docx_with_process(process_id):
    api_key = request.headers.environ.get('HTTP_AUTHORIZATION')
    if api_key is None or not await check_api_key(api_key):
        return ErrorResponseModel("Error api-key", 400, "Invalid api-key")
    process = get_process_by_id(process_id)
    if process is None:
        return ErrorResponseModel("Error process", 400, "Process not Found")
    if process["file_type"] != "docx":
        return ErrorResponseModel("Error process", 400, "The template file type does not match the api request")
    if request.files.get('file', None):
        json_file = request.files['file']
        if not json_file.filename.endswith('.json'):
            return ErrorResponseModel("Error data", 400, "Invalid file type")
        list_filenames = await create_filenames_for_docx()
        await start_create_docx_with_process(process_id, json_file, list_filenames, True)
        # Открытие сохранённого готового файла
        save_file = open(os.path.join(app.config['UPLOAD_FOLDER'], list_filenames[2]), 'rb')
        file = save_file.read()
        save_file.close()
        await delete_template_file(list_filenames[0], list_filenames[1], list_filenames[2])
        # Подготовка ответа
        response = make_response(file)
        _type = mimetypes.guess_type(list_filenames[2])
        response.mimetype = _type[0]
        return response


# Генерация документа отложенным способом со стороны стороннего сервиса через api
@docx.route("/api/generate/file-docx/<process_id>", methods=['POST'])
async def api_file_docx_with_process(process_id):
    api_key = request.headers.environ.get('HTTP_AUTHORIZATION')
    if api_key is None or not await check_api_key(api_key):
        return ErrorResponseModel("Error api-key", 400, "Invalid api-key")
    process = get_process_by_id(process_id)
    if process is None:
        return ErrorResponseModel("Error process", 400, "Process not Found")
    if process["file_type"] != "docx":
        return ErrorResponseModel("Error process", 400, "The template file type does not match the api request")
    if request.files.get('file', None):
        json_file = request.files['file']
        if not json_file.filename.endswith('.json'):
            return ErrorResponseModel("Error data", 400, "Invalid file type")
        list_filenames = await create_filenames_for_docx()
        file_id = await start_create_docx_with_process(process_id, json_file, list_filenames)
        # Подготовка ответа
        response = Response()
        response.status_code = 202
        response.location = request.host_url + url_for('process.download_docx_result_file_api', file_id=file_id)
        return response
    return ErrorResponseModel("Error data", 400, "File not Found")


# Генерация документа со стороны web-приложения
@docx.route("/generate/file-docx/<process_id>", methods=['POST'])
@login_required
async def file_docx(process_id):
    if request.files.get('file', None):
        json_file = request.files['file']
        if not json_file.filename.endswith('.json'):
            flash('Файл должен быть типа json!')
            return redirect(url_for('process.open_process', id=process_id))
        list_filenames = await create_filenames_for_docx()
        await start_create_docx_with_process(process_id, json_file, list_filenames)
    else:
        flash('Файл не выбран!')
    return redirect(url_for('process.open_process', id=process_id))


# Начало запуска процесса создания документа
async def start_create_docx_with_process(process_id, json_file, list_filenames: list, is_now=False):
    process = get_process_by_id(process_id)
    template_file_id = process['file_id']
    template_file_byte = get_file(template_file_id)
    # Сохранение шаблонного документа на пк
    output = open(os.path.join(app.config['UPLOAD_FOLDER'], list_filenames[0]), 'wb')
    output.write(template_file_byte)
    output.close()
    # Временная загрузка json данных на пк
    json_file.save(os.path.join(app.config['UPLOAD_FOLDER'], list_filenames[1]))
    # Запуск генерации документа
    await docx_worker(list_filenames[0], list_filenames[1], list_filenames[2])
    # Если операция не сиюминутная, то сохранить в БД
    if not is_now:
        # Сохранение готового документа в БД
        file_id = await save_result_file_in_db(list_filenames[2], process_id)
        # Удаление ранее созданных файлов
        await delete_template_file(list_filenames[0], list_filenames[1], list_filenames[2])
        return file_id


# Создание документа из docx
async def docx_worker(template_filename: str, json_filename: str, result_filename: str):
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


# Создание временных имён для файлов
async def create_filenames_for_docx() -> list:
    # Генерация временного имени шаблонного файла
    template_filename = str(uuid.uuid4()) + '.docx'
    # Генерация временного имена готового файла
    result_filename = str(uuid.uuid4()) + '.docx'
    # Генерация временног имени для файла с данными
    json_data_filename = str(uuid.uuid4()) + '.json'
    return [template_filename, json_data_filename, result_filename]
