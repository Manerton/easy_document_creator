from bson import ObjectId
from flask_pymongo import PyMongo
from gridfs import GridFS

from modul_app.main import app
from settings import settings


app.config['MONGO_URI'] = settings.MONGO_URI
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