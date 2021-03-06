# -*- coding: utf-8 -*-


from db import db as _db


def _convert_time(func):
    def wrapper(*args, **kwargs):
        r = func(*args, **kwargs)
        for item in r:
            item['time'] = unicode(item['time'])[0: 16]
        return r

    return wrapper


def collect(user_id, enter_id):
    sql = 'select id from collect_enterprise where user = %s and company = %s' % (user_id, enter_id)
    if _db.query_one(sql) is None:
        _db.insert('collect_enterprise', {'user': user_id, 'company': enter_id})
        return True
    return False


def discollect(user_id, enter_id):
    sql = 'delete from collect_enterprise where user = %s and company = %s' % (user_id, enter_id)
    _db.execute(sql)
    return True


@_convert_time
def get_nearby_enters(city_id, lat, lng, limit_start):
    sub_sql_where = '' if city_id == 0 else 'where e.city = %s ' % city_id
    sub_sql_limit = '' if limit_start == -1 else '%s, ' % limit_start
    sql = 'select ' \
          'e.id, e.company as companyId, e.name, e.address, e.time, e.nick, ' \
          '(6371.004*ACOS(SIN(%s/565.486678)*SIN(e.lat/565.486678)+COS(%s/565.486678)*COS(e.lat/565.486678)*COS((%s-e.lng)/565.486678))) as distance ' \
          'from company_info as e %s ' \
          'order by distance limit %s 10; ' % (lat, lat, lng, sub_sql_where, sub_sql_limit)
    return _db.query(sql)


@_convert_time
def get_user_collect_enters(user_id, start_id):
    sql_limit = '' if start_id == -1 else '%s,' % start_id
    sql = 'select ' \
          'e.id, e.company as companyId, e.name, e.address, e.time, e.nick ' \
          'from company_info as e ' \
          'join collect_enterprise as a on a.company = e.company and a.user = %s ' \
          'order by a.id desc limit %s 10' % (user_id, sql_limit)
    return _db.query(sql)


@_convert_time
def get_hot_enters(city_id, limit_start):
    sub_sql_where = '' if city_id == 0 else 'where e.city = %s ' % city_id
    sub_sql_limit = '' if limit_start == -1 else '%s, ' % limit_start
    sql = 'select * from (select ' \
          'e.id, e.company as companyId, e.name, e.address, e.time, e.nick, e.apply ' \
          'from company_info as e %s order by e.apply desc) as r limit %s 10;' % (sub_sql_where, sub_sql_limit)
    return _db.query(sql)


@_convert_time
def get_all_enters(city_id, limit_start):
    sub_sql_where = '' if city_id == 0 else 'where e.city = %s ' % city_id
    sub_sql_limit = '' if limit_start == -1 else '%s, ' % limit_start
    sql = 'select ' \
          'e.id, e.company as companyId, e.name, e.address, e.time, e.nick ' \
          'from company_info as e %s order by id desc limit %s 10;' % (sub_sql_where, sub_sql_limit)
    return _db.query(sql)


@_convert_time
def search_enters(city_id, enter_name, limit_start):
    sub_sql_where = '' if city_id == 0 else 'and e.city = %s ' % city_id
    sub_sql_limit = '' if limit_start == -1 else '%s, ' % limit_start
    sql = 'select ' \
          'e.id, e.company as companyId, e.name, e.address, e.time, e.nick ' \
          'from company_info as e where (e.name like "%%%s%%" or e.nick like "%%%s%%") %s order by id desc limit %s 10;' % (
              enter_name, enter_name, sub_sql_where, sub_sql_limit)
    return _db.query(sql)


def get_enter_info(enterprise_id):
    sql = 'select ' \
          'e.id, e.company as companyId, e.name, e.address, ' \
          'e.time, e.nick, e.introduction, e.jobs, e.apply, e.collect ' \
          'from company_info as e where e.company = %s' % enterprise_id
    r = _db.query_one(sql)
    if r is not None:
        r['time'] = unicode(r['time'])[0: 10]
    return r


def is_enterprise_collected(user_id, enterprise_id):
    sql = 'select id from collect_enterprise where user = %s and company = %s' % (user_id, enterprise_id)
    return _db.query_one(sql) is not None
