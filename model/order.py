#!/usr/bin/env python
# -*- coding:utf8 -*-

from sqlalchemy import (
    BigInteger, Column, DateTime, Date,
    Integer, String, text, Sequence, Index, SmallInteger,create_engine
)

from model.base import Base



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
    channel = Column(String(12),nullable=False,server_default=text("wx"))
