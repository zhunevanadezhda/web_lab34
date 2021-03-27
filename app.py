# coding=utf-8
import re
import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from entities import User, Task
from storage import Storage

# Создаём приложение
app = Flask(__name__)

# Конфигурируем
# Устанавливаем ключ, необходимый для шифрования куки сессии
app.secret_key = b'_5#y2L"F4Q8ziDec]/'


# Описываем основные маршруты и их обработчики

# Главная страница
@app.route('/', methods=['GET'])
def home():
    # Email получаем из сессии
    user = None
    task = None
    lenlist = 0
    if 'user_id' in session:
        user_id = session['user_id']
        user = Storage.get_user_by_id(user_id)
        task = Storage.get_task_by_id(user_id)
        if task:
            lenlist = len(task)
    return render_template('pages/index.html', user=user, len=lenlist, task=task)


# Страница с формой входа
@app.route('/login', methods=['GET'])
def login():
    if 'user_id' in session:
        return redirect('/')
    return render_template('pages/login.html', page_title='Auth Example')


# Обработка формы входа
@app.route('/login', methods=['POST'])
def login_action():
    page_title = 'Вход'

    # Введённые данные получаем из тела запроса
    if not request.form['email']:
        return render_template('pages/login.html', page_title=page_title, error='Требуется ввести email')
    if not request.form['password']:
        return render_template('pages/login.html', page_title=page_title, error='Требуется ввести пароль')

    # Ищем пользователя в БД с таким email паролем
    user = Storage.get_user_by_email_and_password(request.form['email'], request.form['password'])

    # Неверный пароль
    if not user:
        return render_template('pages/login.html', page_title=page_title, error='Неверный пароль')

    # Сохраняем пользователя в сессии
    session['user_id'] = user.id

    # Перенаправляем на главную страницу
    return redirect(url_for('home'))


# Добавление/удаление задачи
@app.route('/', methods=['POST', 'DELETE', 'PATCH'])
def home_action():
    lenlist = 0
    user_id = session['user_id']
    user = Storage.get_user_by_id(user_id)
    # AJAX Delete
    if request.method == 'DELETE':
        search = request.get_json()
        Storage.del_task(user_id, search['task_id'])
        return jsonify(search)
    # AJAX Update
    if request.method == 'PATCH':
        search = request.get_json()
        if 'action' in search.keys():
            Storage.update_task_status(search['task_id'], search['action'])
        else:
            Storage.update_task(search['task_id'], search['task_name'], search['task_description'])
        return "success", 200
    task = Storage.get_task_by_id(user_id)
    if task:
        lenlist = len(task)
    if not request.form['task_name']:
        return render_template('pages/index.html', user=user, task=task, len=lenlist,
                               error="Введите название для задачи")
    if not request.form['task_description']:
        return render_template('pages/index.html', user=user, task=task, len=lenlist,
                               error="Введите описание для задачи")
    Storage.add_task(Task(None, request.form['task_name'], request.form['task_description'], None), user_id)
    return redirect(url_for('home'))


# Получение данных для редактирования задачи
@app.route('/change/<int:id>', methods=['GET'])
def change(id):
    change_task = Storage.find_task(id)
    if change_task is not None:
        return json.dumps(change_task.serialize())
    return redirect(url_for('home'))


# Получение задачи
@app.route('/getTasks', methods=['GET'])
def get_tasks():
    user_id = session['user_id']
    task = Storage.get_task_by_id(user_id)
    taskList = []
    for t in task:
        taskList.append(Task(t[0], t[1], t[2], t[3]).serialize())
    return json.dumps(taskList)


# Форма регистрации
@app.route('/registration', methods=['GET'])
def registration():
    return render_template('pages/registration.html', page_title='Регистрация')


# Обработка формы регистрации
@app.route('/registration', methods=['POST'])
def registration_action():
    page_title = 'Регистрация'
    error = None
    # Проверяем данные
    if not request.form['email']:
        error = 'Требуется ввести Email'
    if not request.form['password']:
        error = 'Требуется ввести пароль'
    if not request.form['password2']:
        error = 'Требуется ввести повтор пароля'
    if request.form['password'] != request.form['password2']:
        error = 'Пароли не совпадают'
    if Storage.is_user_registred(request.form['email']):
        error = 'Пользователь с таким email уже зарегистрирован'
    pattern_password = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$')
    if not pattern_password.match(request.form['password']):
        error = 'Пароль должен быть от 8-ми до 20 символов, содержать хотя бы одно число, ' \
                'хотя бы одну латинскую букву в нижнем и верхнем регистре, хотя бы один спец символ'

    # В случае ошибки рендерим тот же шаблон, но с текстом ошибки
    if error:
        return render_template('pages/registration.html', page_title=page_title, error=error)

    # Добавляем пользователя
    Storage.add_user(User(None, request.form['email'], request.form['password']))

    # Перенаправляем на главную
    return redirect(url_for('home'))


# Выход пользователя
@app.route('/logout')
def logout():
    # Просто выкидываем его из сессии
    session.pop('user_id')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.env = 'development'
    app.run(port=2020, host='127.0.0.1', debug=True)
