import os
import settings
from settings import settings
from flask import Flask
import webview
from flask_login import LoginManager
from modul_app.models.user import User

app = Flask(__name__)
app.secret_key = os.urandom(24)

# папка для сохранения загруженных файлов
app.config['UPLOAD_FOLDER'] = settings.UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

web = webview.create_window('project', app)

import modul_app.database
from modul_app.database.user_repository import get_user_by_id


@login_manager.user_loader
def load_user(user_id):
    find_user = get_user_by_id(user_id)
    return User(find_user["name"], find_user["email"], find_user["password"], find_user["id"])


from modul_app.controller.auth_controller import auth as auth_blueprint

app.register_blueprint(auth_blueprint)

from modul_app.controller.docx_controller import docx as docx_blueprint

app.register_blueprint(docx_blueprint)

from modul_app.controller.user_controller import user as user_blueprint

app.register_blueprint(user_blueprint)

from modul_app.controller.xlsx_controller import xlsx as xlsx_blueprint

app.register_blueprint(xlsx_blueprint)

from modul_app.controller.main_controller import main as main_blueprint

app.register_blueprint(main_blueprint)

from modul_app.controller.process_controller import process as process_blueprint

app.register_blueprint(process_blueprint)

from modul_app.controller.api_key_controller import api_key as api_key_blueprint

app.register_blueprint(api_key_blueprint)


