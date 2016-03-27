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
def get_user_jobs(user_id, start_id):
    sql_limit = '' if start_id == -1 else '%s,' % start_id
    sql = 'select ' \
          'j.id, j.name, j.address, j.time, j.company as companyId , c.name as company ,c.nick, a.status ' \
          'from job as j ' \
          'join apply_job as a on a.job = j.id and a.user = %s ' \
          'join company_info as c on j.company = c.company order by a.id desc limit %s 10 ' % (user_id, sql_limit)
    return _db.query(sql)


@_convert_time
def get_user_collect_jobs(user_id, start_id):
    sql_where = '' if start_id == -1 else '%s,' % start_id
    sql = 'select ' \
          'j.id, j.name, j.address, j.time, j.company as companyId , c.name as company ,c.nick ' \
          'from job as j ' \
          'join collect_job as a on a.job = j.id and a.user = %s ' \
          'join company_info as c on j.company = c.company order by a.id desc limit %s 10 ' % (user_id, sql_where)
    return _db.query(sql)


def apply_job(user_id, job_id):
    sql = 'select id from apply_job where user = %s and job = %s' % (user_id, job_id)
    if _db.query_one(sql) is None:
        _db.insert('apply_job', {'user': user_id, 'job': job_id})
        _db.execute('update job set apply = apply + 1 where id = %s' % job_id)
        r = _db.query_one('select company from job where id = %s' % job_id)
        _db.execute('update company_info set apply = apply + 1 where company = %s' % r['company'])
        return True
    return False


def collect_job(user_id, job_id):
    sql = 'select id from collect_job where user = %s and job = %s' % (user_id, job_id)
    if _db.query_one(sql) is None:
        _db.insert('collect_job', {'user': user_id, 'job': job_id})
        _db.execute('update job set collect = collect + 1 where id = %s' % job_id)
        return True
    return False


def discollect(user_id, job_id):
    sql = 'delete from collect_job where user = %s and job = %s' % (user_id, job_id)
    _db.execute('update job set collect = collect - 1 where id = %s' % job_id)
    _db.execute(sql)
    return True


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


def get_user_job_status(job_id, user_id):
    sql = 'select id from apply_job where job = %s and user = %s' % (job_id, user_id)
    is_apply = True if _db.query_one(sql) is not None else False
    sql = 'select id from collect_job where job = %s and user = %s' % (job_id, user_id)
    is_collect = True if _db.query_one(sql) is not None else False
    return {'apply': is_apply, 'collect': is_collect}


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


@_convert_time
def get_enter_jobs(enterprise_id, start_id):
    sql_where_id = '' if start_id < 1 else 'and j.id < %s' % start_id
    sql = 'select ' \
          'j.id, j.name, j.address, j.time, j.company as companyId , c.name as company ,c.nick ' \
          'from job as j ' \
          'join company_info as c ' \
          'on j.company = c.company and c.company = %s %s order by id desc limit 10;' % (enterprise_id, sql_where_id)
    return _db.query(sql)
