import flask_pymongo
from bson import ObjectId

from app.database.db import db, put_file_database, get_file_database, delete_file_database

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




