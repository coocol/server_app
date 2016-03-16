# -*- coding: utf-8 -*-

from db import db
from util import util


def is_phone_existed(phone):
    return db.exist('select phone from user where phone = %s and pass = 1' % phone)


def save_new_user(phone):
    if db.exist('select id from user where phone = %s' % phone):
        db.execute('delete from user where phone = %s' % phone)
    db.insert(table='user', values={'phone': phone})
    return db.query('select id from user where phone = %s' % phone)[0]


def save_phone_password(phone, code):
    db.insert(table='password_code', values={'phone': phone, 'code': code})


def change_phone_password(phone, password, code):
    if db.exist('select id from password_code where phone = %s and code = %s' % (phone, code)):
        salt = util.generate_salt()
        db.execute('update user set password = "%s", salt = "%s" where phone = "%s"'
                   % (util.bcrypt_password(password + salt), salt, phone))
        return True
    return False


def confirm_phone_password_code(phone, code):
    return db.exist('select id from password_code where phone = %s and code = %s' % (phone, code))


def save_phone_code(user, phone, code):
    if db.exist('select id from phone_code where phone = %s' % phone):
        db.execute('delete from phone_code where phone = %s' % phone)
    db.insert(table='phone_code', values={'user': user, 'phone': phone, 'code': code})


def register_user(phone, password):
    token = util.generate_access_token(password)
    salt = util.generate_salt()
    db.execute('update user set token = "%s", password = "%s", salt = "%s", pass = 1 where phone = "%s"'
               % (token, util.bcrypt_password(password + salt), salt, phone))
    uid = db.query_one('select id from user where phone = %s' % phone)['id']
    db.insert('user_settings', {'user': uid})
    db.insert('user_info', {'user': uid})


def check_code(phone, code):
    return db.exist('select id from phone_code where phone=%s and code=%s' % (phone, code))


def get_token(phone, password):
    r = db.query_one('select password, salt from user where phone = %s and pass=1' % phone)
    if r is not None and util.bcrypt_check(password=password + r['salt'], hashed=r['password']):
        new_token = util.generate_access_token(password)
        db.execute('update user set token = "%s" where phone = "%s"' % (new_token, phone))
        return db.query_one(
            'select user.id, user.phone, user.token, user_settings.city, user_settings.cityId, user_settings.appliable '
            'from user join user_settings on user_settings.user = user.id where user.phone = %s' % phone)
    return None


def get_locations():
    cities = db.query('select * from cities')
    provinces = db.query('select * from provinces')
    return {'cities': cities, 'provinces': provinces}


def check_token(uid, token):
    u = db.query_one('select token from user where id = %s' % uid)
    return u is not None and u['token'] == token


def modify_user_settings(uid, values):
    db.update(table='user_settings', conditions={'user': uid}, values=values)


# def refresh_all_jobs(city_id):
#     if city_id == 0:
#         sql = 'select ' \
#               'j.id, j.name, j.address, j.time, j.company as companyId , c.name as company, c.nick ' \
#               'from job as j ' \
#               'join company_info as c ' \
#               'on j.company = c.company ' \
#               'order by id desc limit 10;'
#     else:
#         sql = 'select ' \
#               'j.id, j.name, j.address, j.time, j.company as companyId , c.name as company, c.nick ' \
#               'from job as j ' \
#               'join company_info as c ' \
#               'on j.company = c.company and j.city = %s order by id desc limit 10;' % city_id
#     r = db.query(sql)
#     if r is not None:
#         for item in r:
#             item['time'] = unicode(item['time'])[0: 16]
#     return r
#
#
# def refresh_hot_jobs(city_id):
#     if city_id == 0:
#         sql = 'select ' \
#               'j.id, j.name, j.address, j.time, j.apply, j.company as companyId , c.name as company, c.nick ' \
#               'from job as j ' \
#               'join company_info as c ' \
#               'on j.company = c.company ' \
#               'order by j.apply desc limit 10;'
#     else:
#         sql = 'select ' \
#               'j.id, j.name, j.address, j.time, j.apply, j.company as companyId , c.name as company ,c.nick ' \
#               'from job as j ' \
#               'join company_info as c ' \
#               'on j.company = c.company and j.city = %s order by j.apply desc limit 10;' % city_id
#     r = db.query(sql)
#     if r is not None:
#         for item in r:
#             item['time'] = unicode(item['time'])[0: 16]
#     return r
#
#
# def get_all_jobs(start_id, city_id):
#     if city_id == 0:
#         sql = 'select ' \
#               'j.id, j.name, j.address, j.time, j.company as companyId , c.name as company, c.nick ' \
#               'from job as j ' \
#               'join company_info as c ' \
#               'on j.company = c.company and j.id < %s order by id desc limit 10;' % start_id
#     else:
#         sql = 'select ' \
#               'j.id, j.name, j.address, j.time, j.company as companyId , c.name as company ,c.nick ' \
#               'from job as j ' \
#               'join company_info as c ' \
#               'on j.company = c.company and j.id < %s and j.city = %s order by id desc limit 10;' % (start_id, city_id)
#     r = db.query(sql)
#     if r is not None:
#         for item in r:
#             item['time'] = unicode(item['time'])[0: 16]
#     return r
#
#
# def get_hot_jobs(start_id, city_id):
#     if city_id == 0:
#         sql = 'select * from (select ' \
#               'j.id, j.name, j.address, j.time, j.company as companyId ,j.apply, c.name as company , c.nick ' \
#               'from job as j ' \
#               'join company_info as c ' \
#               'on j.company = c.company order by j.apply desc) as r limit %s, 10;' % start_id
#     else:
#         sql = 'select * from (select ' \
#               'j.id, j.name, j.address, j.time, j.company as companyId ,j.apply, c.name as company ,c.nick ' \
#               'from job as j ' \
#               'join company_info as c ' \
#               'on j.company = c.company and j.city = %s order by j.apply desc) as r limit %s, 10;' % (city_id, start_id)
#     r = db.query(sql)
#     if r is not None:
#         for item in r:
#             item['time'] = unicode(item['time'])[0: 16]
#     return r
#
#
# def refresh_all_enters(city_id):
#     if city_id == 0:
#         sql = 'select ' \
#               'e.id, e.company as companyId, e.name, e.address, e.time, e.nick ' \
#               'from company_info as e ' \
#               'order by id desc limit 10;'
#     else:
#         sql = 'select ' \
#               'e.id, e.company as companyId, e.name, e.address, e.time, e.nick ' \
#               'from company_info as e where e.city = %s order by id desc limit 10;' % city_id
#     r = db.query(sql)
#     if r is not None:
#         for item in r:
#             item['time'] = unicode(item['time'])[0: 16]
#     return r
#
#
# def get_all_enters(start_id, city_id):
#     if city_id == 0:
#         sql = 'select ' \
#               'e.id, e.company as companyId, e.name, e.address, e.time, e.nick ' \
#               'from company_info as e where e.id < %s order by id desc limit 10;' % start_id
#     else:
#         sql = 'select ' \
#               'e.id, e.company as companyId, e.name, e.address, e.time, e.nick ' \
#               'from company_info as e where e.id < %s and e.city = %s order by id desc limit 10;' % (start_id, city_id)
#     r = db.query(sql)
#     if r is not None:
#         for item in r:
#             item['time'] = unicode(item['time'])[0: 16]
#     return r
#
#
# def refresh_hot_enters(city_id):
#     if city_id == 0:
#         sql = 'select ' \
#               'e.id, e.company as companyId, e.name, e.address, e.time, e.nick, e.apply ' \
#               'from company_info as e ' \
#               'order by e.apply desc limit 10;'
#     else:
#         sql = 'select ' \
#               'e.id, e.company as companyId, e.name, e.address, e.time, e.nick, e.apply ' \
#               'from company_info as e where e.city = %s order by e.apply desc limit 10;' % city_id
#     r = db.query(sql)
#     if r is not None:
#         for item in r:
#             item['time'] = unicode(item['time'])[0: 16]
#     return r
#
#
# def get_hot_enters(start_id, city_id):
#     if city_id == 0:
#         sql = 'select * from (select ' \
#               'e.id, e.company as companyId, e.name, e.address, e.time, e.nick, e.apply ' \
#               'from company_info as e order by e.apply desc) as r limit %s,10;' % start_id
#     else:
#         sql = 'select * from (select ' \
#               'e.id, e.company as companyId, e.name, e.address, e.time, e.nick, e.apply ' \
#               'from company_info as e where e.city = %s order by e.apply desc) as r limit %s, 10;' % (city_id, start_id)
#     r = db.query(sql)
#     if r is not None:
#         for item in r:
#             item['time'] = unicode(item['time'])[0: 16]
#     return r


if __name__ == '__main__':
    print refresh_all_jobs(0)


