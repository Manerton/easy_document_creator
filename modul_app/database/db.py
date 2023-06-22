from bson import ObjectId
from flask_pymongo import PyMongo
from gridfs import GridFS

from modul_app.main import app


app.config['MONGO_URI'] = "mongodb://localhost:27017/EDCDB"
mongo_client = PyMongo(app)
db = mongo_client.db
# Место хранения файлов
storage = GridFS(db, "fs")


# Добавление файлов
def put_file_database(file, filename):
    return storage.put(file, filename=filename)


# Извлечение файлов
def get_file_database(id: ObjectId):
    return storage.get(id).read()


def delete_file_database(id: ObjectId):
    storage.delete(id)