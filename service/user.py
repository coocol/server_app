# -*- coding: utf-8 -*-

from db import db as _db


def _convert_time(func):
    def wrapper(*args, **kwargs):
        r = func(*args, **kwargs)
        for item in r:
            item['time'] = unicode(item['time'])[0: 16]
        return r

    return wrapper


def get_user_info(user_id):
    sql = 'select u.user as Id, u.nick, u.signature, p.phone ' \
          'from user_info as u join user as p on p.id = u.user and u.user = %s' % user_id
    return _db.query_one(sql)


def change_nick(user_id, nick):
    sql = 'update user_info set nick = "%s" where user = %s' % (nick, user_id)
    _db.execute(sql)


def upload_resume(user_id, file_name):
    if _db.query_one('select id from resume where user = %s' % user_id) is None:
        _db.insert('resume', {'user': user_id})
    _db.execute('update resume set file = "%s" where user = %s' % (file_name, user_id))


def change_signature(user_id, signature):
    sql = 'update user_info set signature = "%s" where user = %s' % (signature, user_id)
    _db.execute(sql)


@_convert_time
def get_notifications(user_id, start_id):
    sql_limit = '%s, ' if start_id > 0 else ''
    sql = 'select id, time, job as jobId, company as companyId, status, ' \
          'job_name as jobName, company_name as companyName, type ' \
          'from notification_user where user = %s order by id desc limit %s 10' % (user_id, sql_limit)
    return _db.query(sql)


def is_apply(user_id):
    sql = 'select id from resume where user = %s and name is not null and phone is not null and email is not null' % \
          user_id
    return True if _db.query_one(sql) is not None else False


def get_resume(user_id):
    sql = 'select id, phone, email, birthday, college, college_time as collegeTime, experience, profess, ' \
          'gender, place, hometown, award, english, description, file, name ' \
          'from resume where user = %s ' % user_id
    return _db.query_one(sql)


def update_resume(user_id, field, value):
    if _db.query_one('select id from resume where user = %s' % user_id) is None:
        _db.insert('resume', {'user': user_id})
    _db.execute('update resume set %s = "%s" where user = %s' % (field, value, user_id))


def delete_notifications(user_id, n_id):
    sql = 'delete from notification_user where id = %s and user = %s' % (n_id, user_id)
    _db.execute(sql)
    return True