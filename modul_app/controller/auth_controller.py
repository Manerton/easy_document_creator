from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from modul_app.models.user import User
from modul_app.database.user_repository import (
    check_user,
    get_user_by_email,
    insert_user,
)


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
async def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    find_user = await get_user_by_email(email)
    # Если пользователь не найден или пароль не верный, то вывести ошибку
    if not find_user or not check_password_hash(find_user['password'], password):
        flash('Логин или пароль введены не верно')
        return redirect(url_for('auth.login'))
    user = User(find_user["name"], find_user["email"], find_user["password"], find_user["id"])
    login_user(user, remember=remember)
    return redirect(url_for('process.processes'))


@auth.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
async def signup_post():
    email = request.form.get('email')
    existing_user = await check_user(email)
    if existing_user == False:
        name = request.form.get('name')
        password = request.form.get('password')
        if name and email and password:
            _hash_password = generate_password_hash(password)
            user = User(name, email, _hash_password)
            await insert_user(user.__dict__)
            return redirect(url_for('auth.login'))
        else:
            flash('Поле не заполнено')
            return redirect(url_for('auth.signup'))
    else:
        flash('Пользователь с таким email уже существует')
        return redirect(url_for('auth.signup'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.start_page'))
