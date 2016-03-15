# -*- coding: utf-8 -*-

"""
    send sms to a phone number with a sms_param
"""

import hashlib
import requests
from util import util
import sys
import time

reload(sys)
sys.setdefaultencoding('utf8')

url = 'http://gw.api.taobao.com/router/rest'


def _sign(parameters, secret='9e9544e77a61c18a53bbd88216069f00'):
    """
        signature method
    :param secret: app_secret
    :param parameters: string or dictionary
    """
    if hasattr(parameters, "items"):
        keys = parameters.keys()
        keys.sort()
        parameters = "%s%s%s" % (secret,
                                 ''.join('%s%s' % (key, parameters[key]) for key in keys),
                                 secret)
    sign = hashlib.md5(parameters).hexdigest().upper()
    return sign


def send(rec_num, sms_param):
    """

    :param rec_num: phone number to receive the message
    :param sms_param: template params
    :return: response content
    """
    params = {'app_key': '23322485', 'format': 'json', 'method': 'alibaba.aliqin.fc.sms.num.send',
              'sms_free_sign_name': '锦绣兼职', 'sms_type': 'normal', 'sms_template_code': 'SMS_5540403', 'v': '2.0',
              'sign_method': 'md5', 'rec_num': rec_num, 'sms_param': sms_param, 'timestamp': util.get_current_timestamp()}
    sign = _sign(params)
    params['sign'] = sign
    req = requests.get(url, params=params)
    print req.content
    return req.content


# test
if __name__ == '__main__':
    # print sys.getdefaultencoding()
    while True:
        print send(rec_num='13545398246', sms_param='{"code":"3456"}')
        time.sleep(60)
