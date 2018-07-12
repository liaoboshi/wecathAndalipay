#!/usr/bin/env python
# -*- coding:utf8 -*-

import tornado.web
import os
from server.server import handlers

class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            # 设定 cookie_secret, 用于 secure_cookie
            cookie_secret="e446976943b4e8442f099fed1f3fea28462d5832f483a0ed9a3d5d3859f==78d",
            # 设定 session_secret 用于生成 session_id
            session_secret="3cdcb1f00803b6e78ab50b466a40b9977db396840c28307f428b25e2277f1bcc",
            # memcached 地址
            memcached_address=["127.0.0.1:8021"],
            # session 过期时间
            session_timeout=60,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            login_url="/login",
        )



        # 初始化父类 tornado.web.Application
        tornado.web.Application.__init__(self, handlers=handlers, **settings)
        # 初始化该类的 session_manager
        # self.session_manager = session.SessionManager(settings["session_secret"], settings["memcached_address"],
        #                                                   settings["session_timeout"])



# if __name__ == "__main__":
#     print(os.path.join(os.path.dirname(__file__), "static"))
