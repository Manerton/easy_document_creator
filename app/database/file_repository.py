import flask_pymongo
from bson import ObjectId

from app.database.db import db, put_file_database, get_file_database, delete_file_database

file_collection: flask_pymongo.wrappers.Database = db.MyFiles


def my_file_helper(process) -> dict:
    return {
        "id": str(process["_id"]),
        "filename": process["filename"],
        "template_id": process["template_id"],
        "file_id": process["file_id"]
    }


def get_myfiles(template_id):
    my_files = []
    for my_file in file_collection.find({'template_id': template_id}):
        my_files.append(my_file_helper(my_file))
    return my_files


def get_myfile_by_id(id):
    myfile = file_collection.find_one({'_id': ObjectId(id)})
    if myfile:
        return my_file_helper(myfile)
    return None


def get_file(id):
    return get_file_database(id)


def insert_file(myfile):
    file_collection.insert_one(myfile.__dict__)


def delete_file(id):
    delete_file_database(id)




