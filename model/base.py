#!/usr/bin/env python
# -*- coding:utf8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

# 初始化数据库连接:
# engine = create_engine('postgresql://postgres:123456@10.17.1.207:5432/liao_db',echo=True)
engine = create_engine('postgresql://liao_db:123456@127.0.0.1:5432/mch_order',echo=True)
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)

session = DBSession()