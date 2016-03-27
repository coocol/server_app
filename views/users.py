# -*- coding: utf-8 -*-

from flask import Blueprint, request, send_from_directory
from service import service, user, job, enterprise
import os
import json
from sms import sms
from util import util
from message import msg

users_app = Blueprint("users_app", __name__)


@users_app.route('/api/v1.0/phone/code', methods=['GET'])
def get_sms_code():
    phone = request.args.get('phone', '')
    if service.is_phone_existed(phone):
        return _make_error(msg.PHONE_EXISTED)
    else:
        uid = service.save_new_user(phone=phone)['id']
        code = util.generate_code()
        service.save_phone_code(user=uid, phone=phone, code=code)
        sms.send(rec_num=phone, sms_param='{"code": "%s"}' % code)
        return _make_success({'uid': uid, "code": code})


@users_app.route('/api/v1.0/user', methods=['POST'])
def register():
    data = json.loads(request.data)
    if service.check_code(phone=data['phone'], code=data['code']):
        service.register_user(phone=data['phone'], password=data['password'])
        return _make_success('')


@users_app.route('/api/v1.0/user/<int:user_id>/header', methods=['GET'])
def get_user_header(user_id):
    if service.check_token(user_id, request.args.get('token', '')):
        u = user.get_user_info(user_id)
        if u is not None:
            return _make_success(u)
        else:
            return _make_error('error id')


@users_app.route('/api/v1.0/token', methods=['POST'])
def get_token():
    data = json.loads(request.data)
    r = service.get_token(data['phone'], data['password'])
    if r is not None:
        r['appliable'] = False if r['appliable'] == 0 else True
        return _make_success(r)
    return _make_error(msg.WRONG_ACCOUNT)


@users_app.route('/api/v1.0/account/code', methods=['GET'])
def get_pass_sms_code():
    phone = request.args.get('phone', '')
    if not service.is_phone_existed(phone):
        return _make_error(msg.NOT_REGISTERED)
    else:
        code = util.generate_code()
        service.save_phone_password(phone, code)
        sms.send(rec_num=phone, sms_param='{"code": "%s"}' % code)
        return _make_success({"code": code})


@users_app.route('/api/v1.0/account/code', methods=['POST'])
def confirm_pass_sms_code():
    data = json.loads(request.data)
    if service.confirm_phone_password_code(data['phone'], data['code']):
        return _make_success('')
    else:
        return _make_error('验证码错误')


@users_app.route('/api/v1.0/account/password', methods=['POST'])
def change_password():
    data = json.loads(request.data)
    if service.change_phone_password(phone=data['phone'], password=data['password'], code=data['code']):
        return _make_success('')
    else:
        return _make_error('fail to change password')


@users_app.route('/api/v1.0/user/settings/location', methods=['POST'])
def change_location():
    data = json.loads(request.data)
    if 'token' not in data.keys() or data['token'] is None or not service.check_token(data['uid'], data['token']):
        return _make_error('token error')
    service.modify_user_settings(uid=data['uid'], values=data['values'])
    return _make_success('ok')


@users_app.route('/api/v1.0/applications/<int:user_id>', methods=['GET'])
def get_user_application(user_id):
    if service.check_token(user_id, request.args.get('token', '')):
        start_id = int(request.args.get('start_id', -1))
        r = job.get_user_jobs(user_id, start_id)
        return _make_success(r) if r is not None else _make_error('error id')
    return _make_error('error')


@users_app.route('/api/v1.0/collection/jobs/<int:user_id>', methods=['GET'])
def get_user_collection_jobs(user_id):
    if service.check_token(user_id, request.args.get('token', '')):
        start_id = int(request.args.get('start_id', -1))
        r = job.get_user_collect_jobs(user_id, start_id)
        return _make_success(r) if r is not None else _make_error('error id')
    return _make_error('error')


@users_app.route('/api/v1.0/collection/enterprises/<int:user_id>', methods=['GET'])
def get_user_collection_enters(user_id):
    if service.check_token(user_id, request.args.get('token', '')):
        start_id = int(request.args.get('start_id', -1))
        r = enterprise.get_user_collect_enters(user_id, start_id)
        return _make_success(r) if r is not None else _make_error('error id')
    return _make_error('error')


@users_app.route('/api/v1.0/user/<int:user_id>/profile', methods=['POST'])
def change_profile(user_id):
    data = json.loads(request.data)
    if service.check_token(user_id, data['token']):
        user.change_nick(user_id, data['nick'])
        user.change_signature(user_id, data['signature'])
        return _make_success('')
    return _make_error('error token')


@users_app.route('/api/v1.0/resume/<int:user_id>', methods=["GET"])
def get_resume(user_id):
    if not service.check_token(user_id, request.args.get('token', '')):
        return _make_error('error token')
    r = user.get_resume(user_id)
    return _make_error('no resume') if r is None else _make_success(r)


@users_app.route('/api/v1.0/resume/<int:user_id>', methods=["POST"])
def update_resume(user_id):
    data = json.loads(request.data)
    if not service.check_token(user_id, data['token']):
        return _make_error('error token')
    r = user.update_resume(user_id, data['field'], data['value'])
    return _make_success('')


@users_app.route('/api/v1.0/resume/file', methods=["GET"])
def download_resume():
    user_id = int(request.args.get('user_id', 0))
    token = request.args.get('token', 0)
    if not service.check_token(user_id, token):
        return _make_error('error token')
    return send_from_directory('static', 'resume/Resume_' + str(user_id) + '_' + request.args.get('name', ''))


@users_app.route('/api/v1.0/notifications/<int:user_id>', methods=["GET"])
def get_notifications(user_id):
    token = request.args.get('token', '')
    start_id = int(request.args.get('start_id', 0))
    if not service.check_token(user_id, token):
        return _make_error('error token')
    return _make_success(user.get_notifications(user_id=user_id, start_id=start_id))


@users_app.route('/api/v1.0/notifications/<int:user_id>', methods=["POST"])
def delete_notifications(user_id):
    data = json.loads(request.data)
    if not service.check_token(user_id, data['token']):
        return _make_error('error token')
    user.delete_notifications(user_id=user_id, n_id=data['nid'])
    return _make_success('')


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
