#!/usr/bin/env python
# -*- coding:utf8 -*-

# 查询订单

from xml.dom import minidom
from xml.etree.ElementTree import Element, tostring
import requests
import time
import hashlib

# MCH_ID = '100064492136'
# K = '8C0003BB239DD1B2258B71D2BCD73132'
# OUT_TRADE_NO = '2652124190114816'
# URL = 'http://api.mch.spd.uline.cc/wechat/orders/query'

MCH_ID = '100002254173'
K = '9B9A9AED4AF487DFA0BA13132FD1AE07'
OUT_TRADE_NO = '810000225417320180417163736'
URL = 'http://mapi.bosc.uline.cc/wechat/orders/query'


#生成随机字符串
def create_md5():    #通过MD5的方式创建
    m = hashlib.md5()
    m.update(bytes(str(time.time()),encoding='utf-8'))
    return m.hexdigest()[:30]

# 生成sign
def sign_key(dic):
    sign = hashlib.md5()
    s3 = '&'.join(sorted(['='.join([i, str(v)]) for i, v in dic.items() if v != ''])) + '&key=' + K
    sign.update(s3.encode('utf-8'))
    return sign.hexdigest().upper()

# Turn a simple dict of key/value pairs into XML 生成xml数据
def dict_to_xml(tag, d):
    elem = Element(tag)
    for key, val in d.items():
        child = Element(key)
        child.text = str(val)
        elem.append(child)
    return elem

# 请求参数返回数据
def request_order(r_url,r_dic):
    # 数据转成xml格式
    xml_b = dict_to_xml('xml', r_dic)
    xml_str = tostring(xml_b).decode()

    # 请求
    print(xml_str)
    r = requests.post(url=r_url, data=xml_str)
    rs_xml = r.content.decode()

    print('请求返回的数据', type(rs_xml), rs_xml)
    return rs_xml


check_dic = {}
check_dic['mch_id'] = MCH_ID
check_dic['out_trade_no'] = OUT_TRADE_NO
check_dic['nonce_str'] = create_md5()
check_dic['sign'] = sign_key(check_dic)


request_order(URL,check_dic)