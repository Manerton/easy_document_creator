from flask import render_template, Blueprint, send_from_directory, redirect, url_for
from flask_login import login_required

main = Blueprint('main', __name__)


@main.route("/api-key", methods=['GET'])
def api_keys_page():
    return render_template("api_generate.html")


@main.route("/", methods=['GET'])
def start_page():
    return redirect(url_for('auth.login'))


@main.route("/api", methods=['GET'])
@login_required
def start_test():
    return render_template("test.html")


@main.route('/uploads/<name>')
def download_file(name):
    return send_from_directory('../filedownloads/', name)
