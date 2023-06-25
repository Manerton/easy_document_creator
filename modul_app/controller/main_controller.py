from flask import render_template, Blueprint, send_from_directory, redirect, url_for
from flask_login import login_required, current_user

main = Blueprint('main', __name__)


@main.route("/api-key", methods=['GET'])
def api_keys_page():
    return render_template("api_keys.html")


@main.route("/", methods=['GET'])
def start_page():
    if current_user.is_authenticated:
        return redirect(url_for('process.processes'))
    return redirect(url_for('auth.login'))


@main.route("/about", methods=['GET'])
def about_page():
    return render_template('about_program.html')

@main.route("/documentation", methods=['GET'])
def documentation_page():
    return render_template('documentation.html')

@main.route('/uploads/<name>')
def download_file(name):
    return send_from_directory('../filedownloads/', name)


