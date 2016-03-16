# -*- coding: utf-8 -*-

import hashlib
from service import service
import bcrypt

s = u'7c4a8d09ca3762af61e59520943dc26494f8941b'

pp = u'$2a$12$5eNUkMRe/zqgeuIIl619ru4BQndhXDhSPD1MsR3IDrG.S0A.uqVae'

from util import util
from db import db

p = s + 'ocwcGHnp'

import json
li = []
sentinel = '99' # ends when this string is seen
for line in iter(raw_input, sentinel):
    line = unicode(line.decode('utf-8'))
    li.append(line)


res = json.dumps(li)
for i in res:
    print i
print unicode(res)



