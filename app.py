# -*- coding: utf-8 -*-

"""
    views for android server
"""

import json

from flask import Flask, send_from_directory, request

import config
import os
from service import service
from views.enterprises import enters_app
from views.jobs import jobs_app
from views.users import users_app

error_resp = dict(status='fail', msg='')
success_resp = dict(status='success')

app = Flask(__name__, static_url_path=config.STATIC_PATH)
app.config['HEAD_FOLDER'] = 'static/head'
app.register_blueprint(jobs_app)
app.register_blueprint(enters_app)
app.register_blueprint(users_app)


@app.route('/api/v1.0/static/<path:path>')
def get_static(path):
    return send_from_directory('static', path)


@app.route('/api/v1.0/cities', methods=['GET'])
def get_locations():
    r = service.get_locations()
    return make_success(r)


@app.route('/api/v1.0/resume/document/<int:user_id>', methods=["POST"])
def save_resume_doc(user_id):
    if not service.check_token(user_id, request.form['token']):
        return make_error('error_token')
    f = request.files['file']
    f.save('static/resume/%s.pdf' % user_id)
    return make_success('')


@app.route('/api/v1.0/resume/photo/<int:user_id>', methods=["POST"])
def save_resume_photo(user_id):
    if not service.check_token(user_id, request.form['token']):
        return make_error('error_token')
    f = request.files['file']
    f.save('static/resume/%s.jpg' % user_id)
    return make_success('')


@app.route('/api/v1.0/user/head/<int:user_id>', methods=["POST"])
def save_user_head(user_id):
    if not service.check_token(user_id, request.form['token']):
        return make_error('error_token')
    try:
        f = request.files['file']
        f.save('static/head/%s.jpg' % user_id)
        return make_success('')
    except Exception, e:
        print e.message
        return make_error('')


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
    app.run(host='0.0.0.0', port=7652, debug=True)
