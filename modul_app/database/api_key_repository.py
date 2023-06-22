import hashlib

import flask_pymongo
from bson import ObjectId

from modul_app.database.db import db
from modul_app.models.api_key import ApiKey

api_key_collection: flask_pymongo.wrappers.Database = db.ApiKey


def api_key_helper(api_key) -> dict:
    return {
        "id": api_key["_id"],
        "name": api_key["name"],
        "key": hashlib.sha256(api_key["key"].encode('utf-8')).hexdigest(),
        "user_id": api_key["user_id"]
    }


async def insert_api_key(api_key: ApiKey):
    api_key_collection.insert_one(api_key.__dict__)


async def delete_api_key(api_key_id: str):
    api_key_find = api_key_collection.find_one({"_id": ObjectId(api_key_id)})
    if api_key_find:
        api_key = api_key_collection.delete_one({"_id": ObjectId(api_key_id)})
        return api_key.raw_result


async def get_api_keys(user_id: str):
    api_keys = []
    for api_key in api_key_collection.find({"user_id": user_id}):
        api_keys.append(api_key_helper(api_key))
    return api_keys


async def check_api_key(key):
    api_keys = []
    for api_key in api_key_collection.find():
        api_keys.append(api_key_helper(api_key))
    for api_key in api_keys:
        if api_key["key"] == key:
            return True
    return False



