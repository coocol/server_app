# -*- coding: utf-8 -*-

import hashlib
from service import service
import bcrypt

s = u'7c4a8d09ca3762af61e59520943dc26494f8941b'

pp = u'$2a$12$5eNUkMRe/zqgeuIIl619ru4BQndhXDhSPD1MsR3IDrG.S0A.uqVae'

from util import util

p = s + 'ocwcGHnp'

print service.get_token('13545398246', s)
