# -*- coding: utf-8 -*-

from db import db as _db


def get_user_info(user_id):
    sql = 'select u.user as Id, u.nick, u.signature, p.phone ' \
          'from user_info as u join user as p on p.id = u.user and u.user = %s' % user_id
    return _db.query_one(sql)