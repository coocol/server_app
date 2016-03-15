# -*- coding: utf-8 -*-

"""
    views for android server
"""

from flask import Flask, request, send_from_directory
import json
from util import util
from service import service, job, enterprise, user
from message import msg
from sms import sms
import config

error_resp = dict(status='fail', msg='')
success_resp = dict(status='success')

app = Flask(__name__, static_url_path=config.STATIC_PATH)


@app.route('/api/v1.0/phone/code', methods=['GET'])
def get_sms_code():
    phone = request.args.get('phone', '')
    if service.is_phone_existed(phone):
        return make_error(msg.PHONE_EXISTED)
    else:
        uid = service.save_new_user(phone=phone)['id']
        code = util.generate_code()
        service.save_phone_code(user=uid, phone=phone, code=code)
        sms.send(rec_num=phone, sms_param='{"code": "%s"}' % code)
        return make_success({'uid': uid, "code": code})


@app.route('/api/v1.0/user', methods=['POST'])
def register():
    data = json.loads(request.data)
    if service.check_code(phone=data['phone'], code=data['code']):
        service.register_user(phone=data['phone'], password=data['password'])
        return make_success('')


@app.route('/api/v1.0/token', methods=['POST'])
def get_token():
    data = json.loads(request.data)
    r = service.get_token(data['phone'], data['password'])
    if r is not None:
        r['appliable'] = False if r['appliable'] == 0 else True
        return make_success(r)
    return make_error(msg.WRONG_ACCOUNT)


@app.route('/api/v1.0/account/code', methods=['GET'])
def get_pass_sms_code():
    phone = request.args.get('phone', '')
    if not service.is_phone_existed(phone):
        return make_error(msg.NOT_REGISTERED)
    else:
        code = util.generate_code()
        service.save_phone_password(phone, code)
        sms.send(rec_num=phone, sms_param='{"code": "%s"}' % code)
        return make_success({"code": code})


@app.route('/api/v1.0/account/code', methods=['POST'])
def confirm_pass_sms_code():
    data = json.loads(request.data)
    if service.confirm_phone_password_code(data['phone'], data['code']):
        return make_success('')
    else:
        return make_error('验证码错误')


@app.route('/api/v1.0/account/password', methods=['POST'])
def change_password():
    data = json.loads(request.data)
    if service.change_phone_password(phone=data['phone'], password=data['password'], code=data['code']):
        return make_success('')
    else:
        return make_error('fail to change password')


@app.route('/api/v1.0/user/settings/location', methods=['POST'])
def change_location():
    data = json.loads(request.data)
    if 'token' not in data.keys() or data['token'] is None or not service.check_token(data['uid'], data['token']):
        return make_error('token error')
    service.modify_user_settings(uid=data['uid'], values=data['values'])
    return make_success('ok')


@app.route('/api/v1.0/jobs', methods=['GET'])
def get_jobs():
    start_id = int(request.args.get('start_id', -1))
    city_id = int(request.args.get('city_id', 0))
    q_type = request.args.get('type', '')
    if q_type == 'all':
        return make_success(job.get_all_jobs(city_id=city_id, start_id=start_id))
    elif q_type == 'hot':
        return make_success(job.get_hot_jobs(city_id=city_id, limit_start=start_id))
    elif q_type == 'nearby':
        lat = float(request.args.get('lat', 0))
        lng = float(request.args.get('lng', 0))
        return make_success(job.get_nearby_jobs(city_id=city_id, lat=lat, lng=lng, limit_start=start_id))
    elif q_type == 'search':
        return make_success(
            job.search_job(city_id=city_id, job_name=request.args.get('query', ''), limit_start=start_id))
    return make_error('no more data')


@app.route('/api/v1.0/enterprises', methods=['GET'])
def get_enters():
    start_id = int(request.args.get('start_id', -1))
    city_id = int(request.args.get('city_id', 0))
    q_type = request.args.get('type', '')
    if q_type == 'all':
        return make_success(enterprise.get_all_enters(city_id=city_id, limit_start=start_id))
    elif q_type == 'hot':
        return make_success(enterprise.get_hot_enters(city_id=city_id, limit_start=start_id))
    elif q_type == 'nearby':
        lat = request.args.get('lat', 0)
        lng = request.args.get('lng', 0)
        return make_success(enterprise.get_nearby_enters(city_id=city_id, limit_start=start_id, lat=lat, lng=lng))
    elif q_type == 'search':
        return make_success(
            enterprise.search_enters(city_id=city_id, enter_name=request.args.get('query', ''), limit_start=start_id))
    return make_error('no more data')


@app.route('/api/v1.0/static/<path:path>')
def get_static(path):
    return send_from_directory('static', path)


@app.route('/api/v1.0/cities', methods=['GET'])
def get_locations():
    r = service.get_locations()
    return make_success(r)


def make_error(content):
    error_resp['msg'] = content
    res = json.dumps(error_resp)
    return res


def make_success(data):
    success_resp['data'] = json.dumps(data)
    res = json.dumps(success_resp)
    return res


app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
