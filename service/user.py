# -*- coding: utf-8 -*-

from db import db as _db


def get_user_info(user_id):
    sql = 'select u.user as Id, u.nick, u.signature, p.phone ' \
          'from user_info as u join user as p on p.id = u.user and u.user = %s' % user_id
    return _db.query_one(sql)


def change_nick(user_id, nick):
    sql = 'update user_info set nick = "%s" where user = %s' % (nick, user_id)
    _db.execute(sql)


def change_signature(user_id, signature):
    sql = 'update user_info set signature = "%s" where user = %s' % (signature, user_id)
    _db.execute(sql)


def is_apply(user_id):
    sql = 'select id from resume where user = %s and name is not null and phone is not null and email is not null' % \
          user_id
    return True if _db.query_one(sql) is not None else False


def get_resume(user_id):
    sql = 'select id, phone, email, birthday, college_time as collegeTime, experience, profess, ' \
          'gender, place, hometown, award, english, description, name ' \
          'from resume where user = %s ' % user_id
    return _db.query_one(sql)


def update_resume(user_id, field, value):
    if _db.query_one('select id from resume where user = %s' % user_id) is None:
        _db.insert('resume', {'user': user_id})
    _db.execute('update resume set %s = "%s" where user = %s' % (field, value, user_id))