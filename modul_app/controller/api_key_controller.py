from flask import Blueprint, request, url_for, render_template, redirect, flash
from flask_login import current_user, login_required
from modul_app.database.api_key_repository import (
    get_api_keys,
    insert_api_key,
    delete_api_key
)
import secrets

from modul_app.models.api_key import ApiKey

api_key = Blueprint('api_key', __name__)


@api_key.route('/api_keys', methods=['GET'])
@login_required
async def get_api_keys_data():
    api_keys = await get_api_keys(current_user.id)
    if api_keys:
        return render_template('api_keys.html', api_keys=api_keys)
    return render_template('api_keys.html')


@api_key.route('/api_keys/add', methods=['POST'])
@login_required
async def insert_api_key_data():
    name = request.form.get('name')
    if name:
        # Генерация случайного ключа
        key = secrets.token_urlsafe(16)
        _api_key = ApiKey(name, key, current_user.id)
        await insert_api_key(_api_key)
    else:
        flash('Поле \"Название\" не заполнено')
    return redirect(url_for('api_key.get_api_keys_data'))


@api_key.route('/api_keys/delete/<id>')
@login_required
async def delete_api_key_data(id):
    await delete_api_key(id)
    return redirect(url_for('api_key.get_api_keys_data'))
