from flask import Flask, send_from_directory, render_template

app = Flask(__name__)

# папка для сохранения загруженных файлов
UPLOAD_FOLDER = '../filedownloads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

import controller.docx_controller
import controller.xlsx_controller


@app.route("/api-key", methods=['GET'])
def api_keys_page():
    return render_template("api_generate.html")


@app.route("/", methods=['GET'])
def start_page():
    return render_template("processes.html")


@app.route("/api", methods=['GET'])
def start_test():
    return render_template("index.html")


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory('../filedownloads/', name)
