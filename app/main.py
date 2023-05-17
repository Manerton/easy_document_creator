import os

from flask import Flask
from flask_login import LoginManager

from app.models.user import User

app = Flask(__name__)
app.secret_key = os.urandom(24)

# папка для сохранения загруженных файлов
UPLOAD_FOLDER = '../temp_downloads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from app.database.user_repository import get_user_by_id

@login_manager.user_loader
def load_user(user_id):
    find_user = get_user_by_id(user_id)
    return User(find_user["name"], find_user["email"], find_user["password"], find_user["id"])


import database.db
import controller.auth_controller
import controller.docx_controller
import controller.xlsx_controller
import controller.user_controller
import controller.process_controller


from controller.auth_controller import auth as auth_blueprint

app.register_blueprint(auth_blueprint)

from controller.docx_controller import docx as docx_blueprint

app.register_blueprint(docx_blueprint)

from controller.user_controller import user as user_blueprint

app.register_blueprint(user_blueprint)

from controller.xlsx_controller import xlsx as xlsx_blueprint

app.register_blueprint(xlsx_blueprint)

from controller.main_controller import main as main_blueprint

app.register_blueprint(main_blueprint)

from controller.process_controller import process as process_blueprint

app.register_blueprint(process_blueprint)





