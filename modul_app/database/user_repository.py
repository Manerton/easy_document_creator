import flask_pymongo.wrappers
from bson.objectid import ObjectId
from flask.json import dumps

from modul_app.database.db import db

users_collection: flask_pymongo.wrappers.Database = db.Users


def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "password": user["password"]
    }


async def check_user(email: str):
    user = users_collection.find_one({"email": email})
    if user:
        return True
    return False


def get_users():
    user_list = []
    for user in users_collection.find():
        user_list.append(user_helper(user))
    return user_list


def get_user_by_id(user_id: str):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return user_helper(user)
    return None


async def get_user_by_email(email: str):
    user = users_collection.find_one({"email": email})
    if user:
        return user_helper(user)
    return None


async def insert_user(user_data: dict):
    users_collection.insert_one(user_data)


def update_user(user_id: str, user_data: dict):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user_update = users_collection.update_one(
            {'_id': ObjectId(user_id)}, {'$set': user_data}
        )
        if user_update:
            return True
    return False


def delete_user(user_id: str):
    user = users_collection.delete_one({"_id": ObjectId(user_id)})
    return user.raw_result
