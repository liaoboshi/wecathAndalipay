#!/usr/bin/env python
# -*- coding:utf8 -*-


# 20140118, redis_test_python3.py

# import sys
# print(sys.version)
# import platform
# print(platform.python_version())

import redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)
# r2 = redis.Redis(host='localhost',password='123456', port=6379, db=0)

r.set('name','liaoboshi')
print(r.get('name'))

print(r.keys())


# 管道
pool = redis.BlockingConnectionPool(host='localhost',port=6379)
r3 = redis.Redis(connection_pool=pool)

pipe = r3.pipeline(transaction=True)

r3.set('name','boshi')
r3.set('role','sb')

pipe.execute()
