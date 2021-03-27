# coding=utf-8
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
from entities import User, Task

# Подключаемся к БД
db = mysql.connector.connect(host='localhost', user='root', password='1234', database='web')


class Storage:
    @staticmethod
    def add_user(user: User):
        """объявление пользователя
        :param user:    новый пользователь
        :type user:     User"""
        cursor = db.cursor()
        cursor.execute('INSERT INTO users (email, password) VALUES (%s, %s)',
                   (user.email, generate_password_hash(user.password)))
        db.commit()

    @staticmethod
    def get_user_by_email_and_password(email: str, passwordHash: str):
        """Найти пользователя по email и паролю
        :param email:       электронная почта
        :type email:        str
        :param passwordHash:    хэш пароля
        :type passwordHash:     str
        :return: пользователь
        :rtype: User
        """
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE email=%s', (email,))
        result = cursor.fetchone()
        if result and check_password_hash(result[2], passwordHash):
            return User(id=result[0], email=result[1], password=result[2])
        else:
            return None

    @staticmethod
    def get_user_by_id(id: int):
        """Найти пользователя по id (добавить пользователя в класс)
        :param id:  идентификатор пользователя
        :type id:   int
        :return:    пользователь
        :rtype:     User"""
        cursor = db.cursor(buffered=True)
        # cursor.execute("""SELECT * FROM users WHERE email='%s'""" % email)
        cursor.execute("""SELECT * FROM users WHERE id=%s""", (id,))
        result = cursor.fetchone()
        if result:
            return User(id=result[0], email=result[1], password=result[2])
        else:
            return None

    @staticmethod
    def is_user_registred(email: str) -> bool:
        """Проверка есть ли уже пользователь с таким email
        :param email:       электронная почта
        :type email:        str
        :return:    True/False
        :rtype:     Boolean"""
        cursor = db.cursor(buffered=True)
        # sql = """SELECT * FROM users WHERE email=%s"""
        # cursor.execute("""SELECT * FROM users WHERE email='%s'""" % email)
        # sql = """SELECT * FROM users WHERE email='"""+email+"""'"""
        # sql2 = 'SELECT * FROM users WHERE email= ?'
        cursor.execute('SELECT * FROM users WHERE email=%s', (email,))
        # result = cursor.fetchone()
        if cursor.rowcount > 0:
            return True
        else:
            return False

    @staticmethod
    def get_task_by_id(id):
        """"найти задачи пользоваиеля"""
        cursor = db.cursor()
        cursor.execute("""SELECT tasks.id, tasks.name, tasks.description, tasks.isFinished """
            """FROM users, tasks, UserTask WHERE tasks.id = UserTask.id_t and users.id = UserTask.id_u """
                       """and users.id = %s""", (id,))
        result = cursor.fetchall()
        if result:
            return result
        else:
            return None

    @staticmethod
    def del_task(user_id, task_id):
        """"удалить задачу пользоваиеля"""
        cursor = db.cursor()
        cursor.execute("""DELETE FROM UserTask WHERE id_u = %s and id_t = %s""", (user_id, task_id))
        db.commit()

    @staticmethod
    def add_task(task, user_id):
        """"добавить задачу пользоваиеля"""
        cursor = db.cursor()
        cursor.execute('INSERT INTO tasks (name, description) VALUES (%s, %s)', (task.name, task.description))
        new_id = cursor.lastrowid
        cursor.execute('INSERT INTO UserTask (id_u, id_t) VALUES (%s, %s)', (user_id, new_id))
        db.commit()

    @staticmethod
    def update_task_status(task_id, action):
        """"изменить состояние задачи"""
        cursor = db.cursor()
        if action == "completed":
            cursor.execute("""UPDATE tasks SET isFinished = 1 WHERE id = %s""", (task_id,))
            db.commit()
        if action == "uncompleted":
            cursor.execute("""UPDATE tasks SET isFinished = 0 WHERE id = %s""", (task_id,))
            db.commit()

    @staticmethod
    def get_task_status(task_id):
        """"добавить задачу в класс"""
        cursor = db.cursor()
        cursor.execute("""SELECT * FROM tasks WHERE id = %s""", (task_id,))
        result = cursor.fetchone()
        if result:
            return Task(result[0], result[1], result[2], result[3])
        else:
            return None


    @staticmethod
    def find_task(task_id):
        """"найти задачу пользователя"""
        cursor = db.cursor()
        cursor.execute("""SELECT * FROM tasks WHERE id = %s""", (task_id,))
        result = cursor.fetchone()
        if result:
            return Task(id=result[0], name=result[1], description=result[2], status=result[3])
        else:
            return None

    @staticmethod
    def update_task(task_id, task_name, task_description):
        """"изменить задачу пользователя"""
        cursor = db.cursor()
        cursor.execute("""UPDATE tasks SET name = %s, description = %s WHERE id = %s""", (task_name, task_description, task_id,))
        db.commit()
