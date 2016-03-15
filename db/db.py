# -*- coding: utf-8 -*-


import mysql.connector

config = dict(user='glory', password='Ef6n9UYb#0', database='glory', host='115.28.22.98')


def conn():
    return mysql.connector.connect(**config)


def query(sql):
    print sql
    cnx = conn()
    cursor = cnx.cursor(dictionary=True, buffered=True)
    cursor.execute(sql)
    r = [i for i in cursor]
    cnx.close()
    return r


def query_one(sql):
    r = query(sql)
    if r is not None and len(r) > 0:
        return r[0]
    return None


def exist(sql):
    return len(query(sql)) > 0


def insert(table, values):
    cnx = conn()
    cursor = cnx.cursor()
    count = len(values.keys())
    sql = ('insert into ' + table + ' (' + ','.join(values.keys()) + ') values (' + ','.join(['%s'] * count) + ')')
    print sql
    sql_data = (values.values())
    cursor.execute(sql, sql_data)
    cnx.commit()
    cnx.close()


def update(table, conditions, values):
    cnx = conn()
    cursor = cnx.cursor()
    v = str()
    for key in values.keys():
        v = (v + key + ' = %s,')
    v = v[0: len(v) - 1]
    c = str()
    for condition in conditions.keys():
        c = (c + condition + ' = %s and')
    c = c[0: len(c) - 4]
    sql = 'update ' + table + ' set ' + v + ' where ' + c
    print sql
    sql_data = (values.values() + conditions.values())
    cursor.execute(sql, sql_data)
    cnx.commit()
    cnx.close()


def execute(sql):
    cnx = conn()
    cursor = cnx.cursor()
    cursor.execute(sql)
    cnx.commit()
    cnx.close()


if __name__ == '__main__':
    update('user_info', {'id': 1}, {'gender': '男', 'age': 20})