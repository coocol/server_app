# -*- coding: utf-8 -*-


from db import db as _db


def _convert_time(func):
    def wrapper(*args, **kwargs):
        r = func(*args, **kwargs)
        for item in r:
            item['time'] = unicode(item['time'])[0: 16]
        return r

    return wrapper


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


@_convert_time
def get_enter_jobs(enterprise_id, start_id):
    sql_where_id = '' if start_id < 1 else 'and j.id < %s' % start_id
    sql = 'select ' \
          'j.id, j.name, j.address, j.time, j.company as companyId , c.name as company ,c.nick ' \
          'from job as j ' \
          'join company_info as c ' \
          'on j.company = c.company and c.company = %s %s order by id desc limit 10;' % (enterprise_id, sql_where_id)
    return _db.query(sql)
