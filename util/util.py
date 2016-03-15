# -*- coding: utf-8 -*-

from random import Random
import datetime
import time
import hashlib
import bcrypt


chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
chars_count = len(chars) - 1

nums = '0123456789'

def bcrypt_password(password):
    return bcrypt.hashpw(password, bcrypt.gensalt())


def bcrypt_check(password, hashed):
    return bcrypt.hashpw(unicode(password).encode('utf-8'), unicode(hashed).encode('utf-8')) == hashed


def get_current_timestamp():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')


def _generate_rand_str(length):
    salt = ''
    ran = Random()
    for i in range(0, length):
        salt += chars[ran.randint(0, chars_count)]
    return salt


def generate_code(length=6):
    code = ''
    ran = Random()
    for i in range(0, length):
        code += nums[ran.randint(0, 9)]
    return code


def generate_salt(length=8):
    return _generate_rand_str(length)


def generate_access_token(source_str=None):
    if source_str is None:
        return hashlib.sha1(_generate_rand_str(12) + get_current_timestamp()).hexdigest()
    else:
        return hashlib.sha1(source_str + _generate_rand_str(12) + get_current_timestamp()).hexdigest()




