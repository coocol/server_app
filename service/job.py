# -*- coding: utf-8 -*-

from db import db as _db


def _convert_time(func):
    def wrapper(*args, **kwargs):
        r = func(*args, **kwargs)
        for item in r:
            item['time'] = unicode(item['time'])[0: 16]
        return r

    return wrapper


def get_job_info(job_id):
    sql = 'select ' \
          'j.id, j.name, j.address, j.time, j.apply, j.collect, j.company as companyId, ' \
          'j.content, j.requirement, j.period, j.salary, j.other, c.name as company ,c.nick ' \
          'from job as j ' \
          'join company_info as c ' \
          'on j.company = c.company and j.id = %s;' % job_id
    r = _db.query_one(sql)
    if r is not None:
        r['time'] = unicode(r['time'])[0: 10]
    return r


@_convert_time
def get_all_jobs(city_id, start_id):
    sql_where_city = '' if city_id == 0 else 'and j.city = %s ' % city_id
    sql_where_id = '' if start_id < 1 else 'and j.id < %s' % start_id
    sql = 'select ' \
          'j.id, j.name, j.address, j.time, j.company as companyId , c.name as company ,c.nick ' \
          'from job as j ' \
          'join company_info as c ' \
          'on j.company = c.company %s %s order by id desc limit 10;' % (
              sql_where_id, sql_where_city)
    return _db.query(sql)


@_convert_time
def get_hot_jobs(city_id, limit_start):
    sub_sql_where = '' if city_id == 0 else 'and j.city = %s ' % city_id
    sub_sql_limit = '' if limit_start == -1 else '%s, ' % limit_start
    sql = 'select * from (select ' \
          'j.id, j.name, j.address, j.time, j.company as companyId ,j.apply, c.name as company ,c.nick ' \
          'from job as j ' \
          'join company_info as c ' \
          'on j.company = c.company %s order by j.apply desc) as r limit %s 10;' % (
              sub_sql_where, sub_sql_limit)
    return _db.query(sql)


@_convert_time
def get_nearby_jobs(city_id, lat, lng, limit_start):
    sub_sql_where = '' if city_id == 0 else 'and j.city = %s ' % city_id
    sub_sql_limit = '' if limit_start == -1 else '%s, ' % limit_start
    sql = 'select ' \
          'j.id, j.name, j.address, j.time, j.company as companyId, c.name as company, c.nick, ' \
          '(6371.004*ACOS(SIN(%s/565.486678)*SIN(j.lat/565.486678)+' \
          'COS(%s/565.486678)*COS(j.lat/565.486678)*COS((%s-j.lng)/565.486678))) as distance ' \
          'from job as j ' \
          'join company_info as c ' \
          'on j.company = c.company %s ' \
          'order by distance limit %s 10; ' % (
              lat, lat, lng, sub_sql_where, sub_sql_limit)
    return _db.query(sql)


@_convert_time
def search_job(city_id, job_name, limit_start):
    sub_sql_city = '' if city_id == 0 else 'and j.city = %s ' % city_id
    sub_sql_limit = '' if limit_start == -1 else '%s, ' % limit_start
    sql = 'select ' \
          'j.id, j.name, j.address, j.time, j.company as companyId , c.name as company ,c.nick ' \
          'from job as j ' \
          'join company_info as c ' \
          'on j.company = c.company and j.name like "%%%s%%" %s order by id desc limit %s 10;' % (
              job_name, sub_sql_city, sub_sql_limit)
    return _db.query(sql)


