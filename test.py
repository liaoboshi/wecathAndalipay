#!/usr/bin/env python
# -*- coding:utf8 -*-


# import datetime
#
#
# def n_time():
#     i = datetime.datetime.now()
#     return i.strftime('%Y%m%d%H%M%S')
#
# print(n_time())


# import json
# a = {'a':1}
# print(a,type(a))
# print(json.dumps(a),type(json.dumps(a)))



from threading import Timer
import time

# def func(msg, starttime):
#     print(u'程序启动时刻：', starttime, '当前时刻：', time.time(), '消息内容 --> %s' % (msg))

# 下面的两个语句和上面的 scheduler 效果一样的
# Timer(2, func, ('hello', time.time())).start()
# Timer(3, func, ('world', time.time())).start()



# s = '20170921092615'
#
# def time_end_type(s):
#     if s:
#         l = []
#         l.append(s[:4])
#         l.append(s[4:6])
#         l.append(s[6:8])
#         a = ('-').join(l)
#         l1 = []
#         l1.append(s[8:10])
#         l1.append(s[10:12])
#         l1.append(s[12:14])
#         b = (':').join(l1)
#         c = a + ' ' + b
#         return c
#     else:
#         return None
#
# print(time_end_type(s))



# lst = [2,3,66,4,5,'K','J','q']
# lst = sorted(lst,key=lambda x:ascii(x))
#
# print(lst)


# d = {'a':1,'bbb':2,'cccc':3}
# r_d = {rank:name for name,rank in d.items()}
# print({len(name) for name in r_d.values()})


# ll = [[1,2],[4,8],[6,70,2]]
# print([y for x in ll for y in x])


# d = {'a':True}
# print(d.get('a',False))
# print(d.get('b',False))


def tests(dh=False):
    print(dh)
    return dh


