# cursor.execute("CREATE DATABASE EngBot_Database")

# cursor.execute("CREATE TABLE users (first_name VARCHAR(255), last_name VARCHAR(255))")
# cursor.execute("CREATE TABLE data_eng (id INT AUTO_INCREMENT PRIMARY KEY, theme VARCHAR(144), subtheme VARCHAR(144), description LONGTEXT, link VARCHAR(255),"
#                "photo BLOB)")
# cursor.execute("CREATE TABLE tests_eng (id_quest INT AUTO_INCREMENT PRIMARY KEY, theme VARCHAR(144), question VARCHAR(255) UNIQUE, answer1 VARCHAR(255),"
#                " answer2 VARCHAR(255), answer3 VARCHAR(255), answer4 VARCHAR(255))")

# cursor.execute("ALTER TABLE users ADD (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT UNIQUE)")
# cursor.execute("ALTER TABLE users CHANGE id id INT AUTO_INCREMENT FIRST")

# --------------- Вставить из файла в БД ---------------------------------
# sql = "INSERT INTO data_eng (theme, subtheme, description, link) VALUES (%s, %s,%s, %s)"
# f = open("Info.txt", "r", encoding="utf-8")
#
# val = (f.readline(), f.readline(), f.read(), "https://www.englishdom.com/blog/imya-sushhestvitelnoe-v-anglijskom-yazyke/")
# cursor.execute(sql, val)
# conn.commit()
# print(cursor.rowcount, "запись добавлена.")
# f.close()
# cursor.execute("SELECT description FROM data_eng WHERE subtheme='Future Tense'")
# print(cursor.fetchone()[0])
# ------------------------------------------------------------------------
# --------------- Вывести из БД ---------------------------------
# cursor.execute("SELECT description FROM data_eng WHERE subtheme='Классификация существительных'")
# print(cursor.fetchone()[0])

import mysql.connector

# ЯКЩО ЩО ПОМІНЯТИ НА НАЧАЛЬНИЙ КОД ПРИЄДНАННЯ БД!!!!!!!!!!!!!!!!!!1

class DataConn:

        def __init__(self, user, password, host, port, database):
                """Конструктор"""
                self.user = user
                self.password = password
                self.host = host
                self.port = port
                self.database = database


        def __enter__(self):
                """
                Открываем подключение с базой данных.
                """
                self.conn = mysql.connector.connect(user=self.user, password=self.password, host=self.host,
                                                    port=self.port, database=self.database)
                return self.conn

        def __exit__(self, exc_type, exc_val, exc_tb):
                """
                Закрываем подключение.
                """
                self.conn.close()
                if exc_val:
                        raise

# Декоратор для подключения к БД
def ensure_connection(func):
        """ Декоратор для подключения к СУБД: открывает соединение,
            выполняет переданную функцию и закрывает за собой соединение.
            Потокобезопасно!
        """

        def inner(*args, **kwargs):
                with DataConn(user='root', password='ComeOne288', host='localhost',
                              port='3306', database='engbot_database') as conn:
                        kwargs['conn'] = conn
                        res = func(*args, **kwargs)
                return res
        return inner



@ensure_connection
def init_db(conn, force: bool = False):
        """
        Проверить, что нужные таблицы существуют, иначе создать их
        :param conn: подключение к СУБД
        :param force: явно пересоздать все таблицы
        """
        print(conn)
        cursor = conn.cursor()

        if force:
                cursor.execute('DROP TABLE IF EXISTS users')
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, first_name VARCHAR(255),
                                                  last_name VARCHAR(255), user_id INT UNIQUE)
        ''')
        # Сохранить изменения
        conn.commit()


@ensure_connection
def add_user(conn, first_name: str, last_name: str, user_id: int):
        cursor = conn.cursor()
        sql = "INSERT INTO users (first_name, last_name, user_id) VALUES (%s, %s, %s)"
        val = (first_name, last_name, user_id)
        cursor.execute(sql, val)
        conn.commit()

# add_user(first_name='Adidas', last_name="Nike", user_id=228)