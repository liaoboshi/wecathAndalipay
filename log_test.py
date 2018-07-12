#!/usr/bin/env python
# -*- coding:utf8 -*-

import logging
import logging.handlers


def order_logg(log_name,log_level,log_str):

    LOG_FILE = '%s.log' % log_name

    handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=5)  # 实例化handler
    fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'

    formatter = logging.Formatter(fmt)  # 实例化formatter
    handler.setFormatter(formatter)  # 为handler添加formatter

    logger1 = logging.getLogger(log_name)  # 获取名为tst的logger
    logger1.addHandler(handler)  # 为logger添加handler
    logger1.setLevel(log_level)

    logger1.info(log_str)


order_logg('log_tst',logging.DEBUG,'1234567')
order_logg('log_tst',logging.DEBUG,'222222')
order_logg('log_tst',logging.DEBUG,'3333')
