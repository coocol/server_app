# -*- coding: utf-8 -*-

from flask import Blueprint, request
import json
from service import job, service, user

jobs_app = Blueprint('jobs_view', __name__)


@jobs_app.route('/api/v1.0/jobs', methods=['GET'])
def get_jobs():
    start_id = int(request.args.get('start_id', -1))
    city_id = int(request.args.get('city_id', 0))
    q_type = request.args.get('type', '')
    if q_type == 'all':
        return _make_success(job.get_all_jobs(city_id=city_id, start_id=start_id))
    elif q_type == 'hot':
        return _make_success(job.get_hot_jobs(city_id=city_id, limit_start=start_id))
    elif q_type == 'nearby':
        lat = float(request.args.get('lat', 0))
        lng = float(request.args.get('lng', 0))
        return _make_success(job.get_nearby_jobs(city_id=city_id, lat=lat, lng=lng, limit_start=start_id))
    elif q_type == 'search':
        return _make_success(
            job.search_job(city_id=city_id, job_name=request.args.get('query', ''), limit_start=start_id))
    return _make_error('no more data')


@jobs_app.route('/api/v1.0/job/status/<int:user_id>', methods=['GET'])
def get_user_job_status(user_id):
    if not service.check_token(user_id, request.args.get('token', '')):
        return _make_error('error token')
    return _make_success(job.get_user_job_status(int(request.args.get('job_id', 0)), user_id))


@jobs_app.route('/api/v1.0/job/<int:job_id>', methods=['POST'])
def apply_job(job_id):
    data = json.loads(request.data)
    user_id = data['user_id']
    if not service.check_token(user_id, data['token']):
        return _make_error('error token')
    if data['action'] == 'apply':
        if not user.is_apply(user_id=user_id):
            return _make_error('need resume')
        return _make_success('') if job.apply_job(user_id=user_id, job_id=job_id) else _make_error('applied')
    elif data['action'] == 'collect':
        return _make_success('') if job.collect_job(user_id=user_id, job_id=job_id) else _make_error('collected')
    elif data['action'] == 'discollect':
        return _make_success('') if job.discollect(user_id=user_id, job_id=job_id) else _make_error('')


@jobs_app.route('/api/v1.0/job/<int:job_id>', methods=['GET'])
def get_job_info(job_id):
    r = job.get_job_info(job_id=job_id)
    if r is not None:
        return _make_success(r)
    return _make_error('error id')


_error_resp = dict(status='fail', msg='')
_success_resp = dict(status='success')


def _make_error(content):
    _error_resp['msg'] = content
    res = json.dumps(_error_resp)
    return res


def _make_success(data):
    _success_resp['data'] = json.dumps(data)
    res = json.dumps(_success_resp)
    return res
