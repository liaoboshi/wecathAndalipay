#!/usr/bin/env python
# -*- coding:utf8 -*-

from sqlalchemy import (
    BigInteger, Column, DateTime, Date,
    Integer, String, text, Sequence, Index, SmallInteger,create_engine
)

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()



import datetime
def n_time():
    i = datetime.datetime.now()
    return i.strftime('%Y-%m-%d %H:%M:%S')


class mch_order(Base):
    __tablename__ = 'mch_order'

    id = Column(Integer, primary_key=True)
    out_trade_no = Column(String(32),nullable=False)
    c_time = Column(DateTime,nullable=False,server_default=text("now()"))
    time_end = Column(DateTime,nullable=True)
    total_fee = Column(Integer,nullable=False)
    trade_type = Column(String(20),nullable=False)
    strade_state = Column(String(20),nullable=False)
    mch_id = Column(String(50),nullable=False)



# 初始化数据库连接:
engine = create_engine('postgresql://postgres:123456@10.17.1.207:5432/liao_db',echo=True)
# engine = create_engine('postgresql://liao_db:123456@127.0.0.1:5432/mch_order',echo=True)
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)


session = DBSession()
new_user = mch_order(id=1, out_trade_no='123sdf',c_time=n_time(),\
                        total_fee=1,trade_type='NATIVE', \
                     strade_state='未支付',mch_id='1234232')

# 添加到session:
session.add(new_user)
# 提交即保存到数据库:
session.commit()
# 关闭session:
session.close()


user = session.query(mch_order).filter(mch_order.id==1).one()
print(user.strade_state)
session.close()
