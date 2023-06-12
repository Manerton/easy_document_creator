import os

import flask_pymongo
from bson import ObjectId

from app.database.db import db, put_file_database, get_file_database, delete_file_database
from app.main import app
from app.models.my_file import MyFile

file_collection: flask_pymongo.wrappers.Database = db.MyFiles


def my_file_helper(process) -> dict:
    return {
        "id": str(process["_id"]),
        "filename": process["filename"],
        "process_id": process["process_id"],
        "file_id": process["file_id"]
    }


def get_my_files(process_id):
    my_files = []
    for my_file in file_collection.find({'process_id': process_id}):
        my_files.append(my_file_helper(my_file))
    return my_files


def get_my_file_by_id(id):
    my_file = file_collection.find_one({'_id': ObjectId(id)})
    if my_file:
        return my_file_helper(my_file)
    return None


def get_file(id):
    return get_file_database(id)


def insert_my_file(my_file):
    file_collection.insert_one(my_file.__dict__)


def delete_my_file(my_file_id: str):
    my_file_find = file_collection.find_one({"_id": ObjectId(my_file_id)})
    if my_file_find:
        delete_result_file(my_file_find["file_id"])
        my_file_delete = file_collection.delete_one({"_id": ObjectId(my_file_id)})
        return my_file_delete.raw_result


def delete_result_file(id):
    delete_file_database(id)


# Загружаем файл в базу
async def save_result_file_in_db(result_filename, process_id):
    save_file = open(os.path.join(app.config['UPLOAD_FOLDER'], result_filename), 'rb')
    file = save_file.read()
    file_id = put_file_database(file, filename=result_filename)
    save_file.close()
    my_file = MyFile(result_filename, file_id, process_id)
    insert_my_file(my_file)
    return file_id


# Удаление ранее созданных файлов из папки для временных файлов
async def delete_template_file(template_filename: str, json_filename: str, result_filename: str):
    # Удаляем json с данными
    delete_file_from_temp(os.path.join(app.config['UPLOAD_FOLDER'], json_filename))
    # Удаляем шаблон документа
    delete_file_from_temp(os.path.join(app.config['UPLOAD_FOLDER'], template_filename))
    # Удаляем готовый полученный документ
    delete_file_from_temp(os.path.join(app.config['UPLOAD_FOLDER'], result_filename))


def delete_file_from_temp(path: str):
    if os.path.isfile(path):
        os.remove(path)




