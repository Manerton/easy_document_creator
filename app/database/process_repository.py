import flask_pymongo
from bson import ObjectId

from app.database.db import db, put_file_database, get_file_database, delete_file_database
from app.models.process import Process

processes_collection: flask_pymongo.wrappers.Database = db.processes_collection


def process_helper(process) -> dict:
    return {
        "id": str(process["_id"]),
        "name": process["name"],
        "description": process["description"],
        "file_id": process["file_id"]
    }


# Получение списка процессов пользователя
def get_processes(user_id: str):
    process_list = []
    for process in processes_collection.find({'user_id': user_id}):
        process_list.append(process_helper(process))
    return process_list


# Получение процесса по id
def get_process_by_id(process_id: str):
    process = processes_collection.find_one({'_id': ObjectId(process_id)})
    if process:
        return process_helper(process)
    return None


# Добавление процесса
def insert_process(process):
    processes_collection.insert_one(process.__dict__)


# Обновление процесса
def update_process(id, process):
    filter = {"_id": ObjectId(id)}
    processes_collection.update_one(filter, {"$set": process.__dict__})


# Удаление процесса
def delete_process(process_id: str):
    process_find = processes_collection.find_one({"_id": ObjectId(process_id)})
    if process_find:
        delete_file(process_find["file_id"])
        process = processes_collection.delete_one({"_id": ObjectId(process_id)})
        return process.raw_result


# Добавленеи в базу файла
def put_file(file):
    return put_file_database(file, filename=file.filename)


# Получение файла из базы
def get_file(id):
    file = get_file_database(id)
    return file


# Удаление файла из базы
def delete_file(id):
    delete_file_database(id)

