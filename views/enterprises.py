# -*- coding: utf-8 -*-

from flask import Blueprint, request
from service import enterprise, service, job
import json

enters_app = Blueprint('enters_app', __name__)


@enters_app.route('/api/v1.0/enterprises', methods=['GET'])
def get_enters():
    start_id = int(request.args.get('start_id', -1))
    city_id = int(request.args.get('city_id', 0))
    q_type = request.args.get('type', '')
    if q_type == 'all':
        return _make_success(enterprise.get_all_enters(city_id=city_id, limit_start=start_id))
    elif q_type == 'hot':
        return _make_success(enterprise.get_hot_enters(city_id=city_id, limit_start=start_id))
    elif q_type == 'nearby':
        lat = request.args.get('lat', 0)
        lng = request.args.get('lng', 0)
        return _make_success(enterprise.get_nearby_enters(city_id=city_id, limit_start=start_id, lat=lat, lng=lng))
    elif q_type == 'search':
        return _make_success(
            enterprise.search_enters(city_id=city_id, enter_name=request.args.get('query', ''), limit_start=start_id))
    return _make_error('no more data')


@enters_app.route('/api/v1.0/enterprise/<int:enterprise_id>', methods=['GET'])
def get_enter_info(enterprise_id):
    r = enterprise.get_enter_info(enterprise_id=enterprise_id)
    if r is not None:
        return _make_success(r)
    return _make_error('error id')


@enters_app.route('/api/v1.0/enterprise/status/<int:user_id>', methods=['GET'])
def get_collect_status(user_id):
    if not service.check_token(user_id, request.args.get('token', '')):
        return _make_error('error token')
    if enterprise.is_enterprise_collected(user_id, int(request.args.get('enterprise_id', 0))):
        return _make_success('yes')
    else:
        return _make_success('no')


@enters_app.route('/api/v1.0/enterprise/<int:enterprise_id>/jobs', methods=['GET'])
def get_enter_jobs(enterprise_id):
    start_id = int(request.args.get('start_id', -1))
    r = job.get_enter_jobs(enterprise_id=enterprise_id, start_id=start_id)
    if r is not None:
        return _make_success(r)
    return _make_error('error id')


@enters_app.route('/api/v1.0/enterprise/<int:enterprise_id>', methods=['POST'])
def apply_enters(enterprise_id):
    data = json.loads(request.data)
    user_id = data['user_id']
    if not service.check_token(user_id, data['token']):
        return _make_error('error token')
    if data['action'] == 'collect':
        return _make_success('') if enterprise.collect(user_id, enterprise_id) else _make_error('collected')
    elif data['action'] == 'discollect':
        return _make_success('') if enterprise.discollect(user_id, enterprise_id) else _make_error('')


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