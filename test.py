# cursor.execute("CREATE DATABASE EngBot_Database")

# cursor.execute("CREATE TABLE users (first_name VARCHAR(255), last_name VARCHAR(255))")
# cursor.execute("CREATE TABLE data_eng (id INT AUTO_INCREMENT PRIMARY KEY, theme VARCHAR(144), subtheme VARCHAR(144), description LONGTEXT, link VARCHAR(255),"
#                "photo BLOB)")
# cursor.execute("CREATE TABLE tests_eng (id_quest INT AUTO_INCREMENT PRIMARY KEY, theme VARCHAR(144), question VARCHAR(255) UNIQUE, answer1 VARCHAR(255),"
#                " answer2 VARCHAR(255), answer3 VARCHAR(255), answer4 VARCHAR(255))")

# cursor.execute("ALTER TABLE users ADD (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT UNIQUE)")
# cursor.execute("ALTER TABLE users CHANGE id id INT AUTO_INCREMENT FIRST")
# cursor.execute("UPDATE customers SET address = 'Canyon 123' WHERE address = 'Valley 345'")

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
import re

def main():
    # f = open("Info.txt", "r", encoding="utf-8")
    #
    # print(f.readline())
    # print(f.readline())
    # print(f.read())


    # def foo(conn, *args, **kwargs):
    #     conn += 1
    #     print(conn)
    #     print(args)
    #     print(kwargs)
    #
    # foo(458, 54, 4568, "asd")

    str = 'Gogaas'

    print(re.search(r'\d|\W', str) is not None)

if __name__ == '__main__':
    main()
