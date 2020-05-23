# import time
#
#
# class TimeChecker:
#
#     def __init__(self, name):
#         self.name = name
#
#     def __enter__(self):
#         self.start = self.get_time_in_sec()
#         return self
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         now = self.get_time_in_sec()
#         time_taken = now - self.start  # in seconds
#         print("Time Taken by " + self.name + ": " + str(time_taken))
#
#     def get_time_in_sec(self):
#         return int(round(time.time() * 1000))
#
#
# def test_list_index_func(range_num):
#     lis = [1,2,3,4,5]
#     with TimeChecker('Process 1') as tim:
#         for i in range(range_num):
#             len(lis)-1
#
# test_list_index_func(1000)
# test_list_index_func(10000)
# test_list_index_func(100000)
# test_list_index_func(1000000)
#
# print("Time: O(n)")
# <=============================================================================>

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

    # str = 'Gogaas'
    #
    # print(re.search(r'\d|\W', str) is not None)

    # dictionary = {'Nickolas': 'Flamel', 'Igor': 'Mirik'}
    # x = tuple(dictionary.items())
    # print(x)

    # l = ['asd', ' aswer', 5486, 87984, 54]
    # i = l.index(l[-1])
    # print(i == len(l)-1)

    # info = [('a', 2, 3, 4, 5), ('b', '5321', '86484', '844'), ('c', 684, 5684, 9), ('d', 456, 27, 87), ('f', 98, 89, 564)]
    # # d = {info[key][0]: info[key][1:5] for key in range(len(info))}
    # # print(d)
    # # print(d['a'], ' type is ', type(d['a']))
    # # print(info[1][1:3])
    # l = list(info[0])
    # print(l)

    s1 = [1, 2, 3, 4, 5]
    s2 = [4]
    l = list(set(s1) - set(s2))
    print(l)

if __name__ == '__main__':
    main()


