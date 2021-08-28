# -*- coding: utf-8 -*-
# @Time     : 2019/10/17 11:42 AM
# @Author   : Joe
# @Site     :
# @File     : tools.py
# @Software : PyCharm
# @function : xxxx

import time
import random
import hashlib


def get_key_obj(pkeyobj, pkey_file=None, pkey_obj=None, password=None):
    if pkey_file:
        with open(pkey_file) as fp:
            try:
                pkey = pkeyobj.from_private_key(fp, password=password)
                return pkey
            except:
                pass
    else:
        try:
            pkey = pkeyobj.from_private_key(pkey_obj, password=password)
            return pkey
        except:
            pkey_obj.seek(0)

def unique():
    ctime = str(time.time())
    salt = str(random.random())
    m = hashlib.md5(bytes(salt, encoding='utf-8'))
    m.update(bytes(ctime, encoding='utf-8'))
    return m.hexdigest()
