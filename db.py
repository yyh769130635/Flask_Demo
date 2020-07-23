# Author:peter young
import pymysql

def get_conn():
    return pymysql.connect(
        host='127.0.0.1',
        user="root",
        password="199595",
        database = "python_mysql",
        charset='utf8'
    )


def query_data(sql):
    conn = get_conn()
    #用DictCursor返回的是字典的形式，而不是数组
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        conn.close()


def insert_or_update_date(sql):
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
    finally:
        conn.close()



if __name__=="__main__":

    sql=" insert user (name,sex,age,email) values('daming','male','20','daming@qq.com')"
    insert_or_update_date(sql)

    sql = "select * from user"
    datas=query_data(sql)
    import pprint

    pprint.pprint(datas)