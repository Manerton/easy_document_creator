import uuid

from app.main import app
from flask import request, flash, redirect, url_for, render_template, Blueprint
from app.docx_analyzer import DocxAnalyzer
from werkzeug.utils import secure_filename
import os
import json

from app.database.process_repository import (
    get_process_by_id,
    put_file,
    get_file,
    delete_file
)

from app.database.file_repository import ( insert_file )
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


@docx.route("/api/generate/file-docx/<process_id>", methods=['POST'])
def file_docx(process_id):
    head = request.headers
    if request.files.get('file', None):
        json_file = request.files['file']
        process = get_process_by_id(process_id)
        template_file_id = process['file_id']
        template_file_byte = get_file(template_file_id)
        # Генерация временного имени файла шаблона
        temp_random_filename = str(process_id) + '.docx'
        result_filename = str(uuid.uuid4()) + '.docx'
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
        document = DocxAnalyzer()
        # Инициализация шаблона как документа
        document.open_document(os.path.join(app.config['UPLOAD_FOLDER'], temp_random_filename))
        # Инициализация данных из json
        document.init_data(data)
        # Поиск токенов
        document.start_search_tokens()
        # Замена токенов
        document.start_replace()
        # Сохранение готового файла
        document.save_file(os.path.join(app.config['UPLOAD_FOLDER'], result_filename))
        # Открытие сохранеённого готового файла
        save_file = open(os.path.join(app.config['UPLOAD_FOLDER'], result_filename), 'rb')
        file = save_file.read()
        # Загружаем файл в базу
        file_id = put_file(file, result_filename)
        # Удаление ранее созданных файлов из папки для временных файлов
        # delete_file_from_temp(os.path.join(app.config['UPLOAD_FOLDER'], result_filename))
        # delete_file_from_temp(os.path.join(app.config['UPLOAD_FOLDER'], temp_random_filename))
        # delete_file_from_temp(os.path.join(app.config['UPLOAD_FOLDER'], json_file.filename))
        myFile = MyFile(result_filename, file_id, template_file_id)
        insert_file(myFile)
        return redirect(url_for('process.open_process', id=process_id))
