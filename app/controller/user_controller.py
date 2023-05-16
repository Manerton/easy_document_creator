from flask import request, jsonify, Blueprint
from flask_login import login_required, current_user

from app.database.user_repository import (
    get_users,
    get_user_by_id,
    update_user,
    delete_user
)
from app.models.ResponseModel import ResponseModel, ErrorResponseModel
from app.models.user import User

user = Blueprint('user', __name__)


@user.route('/users', methods=['GET'])
@login_required
def users():
    _users = get_users()
    if _users:
        return ResponseModel(_users, "The list of users was returned successfully")
    return ResponseModel(_users, "Empty list returned")


@user.route('/user/<id>', methods=['GET'])
@login_required
def get_user(id):
    _user = get_user_by_id(id)
    if _user:
        return ResponseModel(_user, "User data was returned successfully")
    return ErrorResponseModel("An error occurred.", 404, "User doesn't exist.")


@user.route('/update_user/<id>')
@login_required
def update_user_data(id):
    email = request.form.get('email')
    name = request.form.get('name')
    if name:
        name = current_user.name
    password = request.form.get('password')
    if password:
        password = current_user.password
    _user = User(name, email, password)
    user_is_updated = update_user(id, _user.__dict__)
    if user_is_updated:
        return ResponseModel(
            "Student with ID: {} name update is successful".format(id), "User data was returned successfully"
        )
    return ErrorResponseModel(
        "An error occurred", 404, "User with id {0} doesn't exist".format(id)
    )


@user.route('/delete_user/<id>', methods=['DELETE'])
@login_required
def delete_user_data(id):
    deleted_user = delete_user(id)
    if deleted_user:
        return ResponseModel(
            "User with ID: {} removed".format(id), "User deleted successfully"
        )
    return ErrorResponseModel(
        "An error occurred", 404, "User with id {0} doesn't exist".format(id)
    )


@user.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found ' + request.url
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp