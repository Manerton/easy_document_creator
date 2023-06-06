import mimetypes

from flask import Blueprint, request, flash, redirect, url_for, render_template, make_response
from flask_login import login_required, current_user
from app.database.process_repository import (
    get_processes,
    get_process_by_id,
    insert_process,
    update_process,
    delete_process,
    put_file,
    get_file,
    delete_file
)

from app.database.file_repository import (
    get_my_files,
    get_my_file_by_id,
    delete_my_file
)
from app.models.process import Process

process = Blueprint('process', __name__)


@process.route('/api/processes', methods=['GET'])
@login_required
def processes():
    _processes = get_processes(current_user.id)
    if _processes:
        return render_template('processes.html', _processes=_processes)
    return render_template('processes.html')


@process.route('/api/processes/process', methods=['GET'])
@process.route('/api/processes/process/<id>', methods=['GET'])
@login_required
def get_process(id=None):
    if id:
        _process = get_process_by_id(id)
        if _process:
            return render_template('process.html', process=_process)
    return render_template('process.html')


@process.route('/api/processes/open_process/<id>', methods=['GET'])
@login_required
def open_process(id):
    _process = get_process_by_id(id)
    my_files = get_my_files(_process['id'])
    if _process:
        return render_template('open_process.html', process=_process, myfiles=my_files)


@process.route('/api/processes/add', methods=['POST'])
@login_required
def insert_process_data():
    if not request.files.get('file', None):
        flash('Файл не выбран!')
        return redirect(url_for('process.get_process'))
    file = request.files['file']
    name = request.form.get('name')
    description = request.form.get('description')
    if name and description and file:
        file_type = file.filename.split('.')[1]
        file_id = put_file(file, file.filename)
        _process = Process(name, description, file_type, file_id, current_user.id)
        insert_process(_process)
        return redirect(url_for('process.processes'))
    flash('Поля не заполнены!')
    return redirect(url_for('process.get_process'))


@process.route('/api/processes/update/<id>', methods=["POST"])
@login_required
def update_process_data(id):
    name = request.form.get('name')
    description = request.form.get('description')
    if not name and not description:
        flash('Поля не заполнены')
        return redirect(url_for('process.get_process', id=id))
    _process = get_process_by_id(id)
    file_id = _process['file_id']
    file_type = _process['file_type']
    if request.files.get('file', None):
        delete_file(file_id)
        file = request.files['file']
        file_id = put_file(file, file.filename)
        file_type = file.filename.split('.')[1]
    new_process = Process(name, description, file_type, file_id, current_user.id)
    update_process(id, new_process)
    return redirect(url_for('process.processes'))


@process.route('/api/processes/delete/<id>')
@login_required
def delete_process_data(id):
    _process = delete_process(id)
    return redirect(url_for('process.processes'))


@process.route('/api/processes/download_file/<id>', methods=['GET'])
@login_required
def download_file(id):
    _process = get_process_by_id(id)
    if _process:
        file = get_file(_process['file_id'])
        response = make_response(file)
        _type = mimetypes.guess_type('result.' + _process['file_type'])
        response.mimetype = _type[0]
        return response
    return redirect(url_for('process.processes'))


@process.route('/api/processes/process/download_file/<id>', methods=['GET'])
@login_required
def download_result_file(id):
    my_file = get_my_file_by_id(id)
    if my_file:
        file = get_file(my_file['file_id'])
        response = make_response(file)
        _type = mimetypes.guess_type(my_file['filename'])
        response.mimetype = _type[0]
        return response
    return redirect(url_for('process.processes'))


@process.route('/api/processes/process/delete_file/<id>')
@login_required
def delete_result_file(id):
    my_file = get_my_file_by_id(id)
    if my_file:
        process_id = my_file["process_id"]
        delete_my_file(id)
        return redirect(url_for('process.open_process', id=process_id))
