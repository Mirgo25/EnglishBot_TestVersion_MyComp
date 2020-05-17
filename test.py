# f = open("Info.txt", "r", encoding="utf-8")
#
# print(f.readline())
# print(f.readline())
# print(f.read())




def foo(conn, *args, **kwargs):
    conn += 1
    print(conn)
    print(args)
    print(kwargs)

foo(458, 54, 4568, "asd")