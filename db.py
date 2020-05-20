from typing import Tuple, Dict
import mysql.connector


DICT_THEMES = {
        1: 'Noun (Имя существительное)',
        2: 'Pronoun (Местоимение)',
        3: 'Adjective/Adverb (Прилагательное/наречие)',
        4: 'Number (Числительное)',
        5: 'Verb (Глагол)',
        6: 'Prepositions/phrasal verbs (Предлоги/фразовые глаголы)',
        7: 'Sentence (Предложение)'
}


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
                        raise exc_val

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
                print("Таблица users была удалена!!!")

        cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, first_name VARCHAR(255),
                                                  last_name VARCHAR(255), user_id INT UNIQUE, level INT)
        ''')
        # Сохранить изменения
        conn.commit()


@ensure_connection
def add_user_to_db(conn, first_name: str, last_name: str, user_id: int):
        cursor = conn.cursor()
        sql = "INSERT INTO users (first_name, last_name, user_id, level) VALUES (%s, %s, %s, 1)"
        val = (first_name, last_name, user_id)
        cursor.execute(sql, val)
        conn.commit()


@ensure_connection
def get_user_from_db(conn, user_id: int):
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}")
        return cursor.fetchone()


@ensure_connection
def delete_user_from_db(conn, user_id: int):
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM users WHERE user_id={user_id}")
        conn.commit()


@ensure_connection
def inc_lvl(conn, user_id: int):
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET level=level+1 WHERE user_id={user_id}")
        conn.commit()


@ensure_connection
def get_lvl(conn, user_id: int):
        cursor = conn.cursor()
        cursor.execute(f"SELECT level FROM users WHERE user_id={user_id}")
        (lvl, ) = cursor.fetchone()
        return lvl


@ensure_connection
def get_info_from_db(conn, user_id: int) -> Tuple[str, Dict[str, str], Dict[str, str]]:
        """
        Получение темы, подтем, описаний подтем и ссылок на каждую подтему.
        :return: Tuple with 1 string and 2 dictionaries.
        """
        lvl = get_lvl(user_id=user_id)
        theme = DICT_THEMES[lvl]
        cursor = conn.cursor()
        cursor.execute(f"SELECT subtheme, description, link FROM data_eng WHERE theme='{theme}'")
        info: list = cursor.fetchall()
        # [info[i][0] for i in range(len(info))]  # Вывести только subtheme
        dict_info = dict(zip([info[i][0] for i in range(len(info))], [info[i][1] for i in range(len(info))]))
        dict_links = dict(zip([info[i][0] for i in range(len(info))], [info[i][2] for i in range(len(info))]))
        return theme, dict_info, dict_links


# level = get_lvl()
print(get_info_from_db(user_id=635625366))
# print(get_lvl(user_id=635625366))