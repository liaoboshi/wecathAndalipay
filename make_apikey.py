#!/usr/bin/env python
# -*- coding:utf8 -*-

import os
import codecs

def gen_randown_mch_pkey(len=32):
    return codecs.encode(os.urandom(len), 'hex').decode()[:len]

print(gen_randown_mch_pkey())


def get_dt_api_key(self):
    query = """select api_key from dt_user where dt_id=%s"""
    api_key = self.db.selectSQL(query, (self.current_user,))[0]
    if not api_key:
        api_key = gen_randown_mch_pkey(32)
        query = """update dt_user set api_key=%s where dt_id=%s;"""
        self.db.executeSQL(query, (api_key, self.current_user))
    return api_key

