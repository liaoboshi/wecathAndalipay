#!/usr/bin/env python
# -*- coding:utf8 -*-


import datetime
import hashlib
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from urllib import parse
from xml.dom import minidom
from xml.etree.ElementTree import Element, tostring

import requests
import tornado.gen
import tornado.ioloop
import tornado.web
from tornado.gen import coroutine
from tornado.httpclient import AsyncHTTPClient

from log_d import error_log,info_log
from model.base import session
from model.order import mch_order
from static.diy_per_page import Diy_page

settings = {
    'template_path':'tmplates',
    'static_path':'static',
    'static_url_prefix':'/static/',
}


#测试用
KURL = 'http://mapi.bosc.uline.cc'
# KURL = 'http://120.78.25.154'
# MCH_ID = '100078521322'
# K = '51FEC88A997C093AE8D773A897966806'

#
MCH_ID = '100002583110'
K = '69422055A20161B28079CE6D6F7C71FB'


# MCH_ID = '100002254173'
# K = '9B9A9AED4AF487DFA0BA13132FD1AE07'

# KURL = 'http://api.mch.spd.uline.cc'
# MCH_ID = '100078520638'
# K = '444B4E09B4786D7355B1DB99F19DCF38'




#PF京东测试的   100015666075
# K1 = '85C0F7501D92B19DB37467AE5F5075FF'

#100015666075（D1商户） 123456
# 85C0F7501D92B19DB37467AE5F5075FF


# 上海
# 100002254173
# 9B9A9AED4AF487DFA0BA13132FD1AE07



class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

# self.write("Hello, world")  # 可以返回字符串
# self.render("s1.html")  # 这个可以返回html
# self.redircet("www.baidu.com")  # 跳转到某个url

#创建订单时间格式
def n_time():
    i = datetime.datetime.now()
    return i.strftime('%Y-%m-%d %H:%M:%S')


#支付完成时间格式转换
def time_end_type(s):
    if s:
        l = []
        l.append(s[:4])
        l.append(s[4:6])
        l.append(s[6:8])
        a = ('-').join(l)
        l1 = []
        l1.append(s[8:10])
        l1.append(s[10:12])
        l1.append(s[12:14])
        b = (':').join(l1)
        c = a + ' ' + b
        return c
    else:
        return None


# 请求参数返回数据
def request_order(r_url,r_dic):
    # 数据转成xml格式
    xml_b = dict_to_xml('xml', r_dic)
    xml_str = tostring(xml_b).decode()

    # 请求
    r = requests.post(url=r_url, data=xml_str)
    rs_xml = r.content.decode()

    print('请求返回的数据', type(rs_xml), rs_xml)
    return rs_xml


# 生成sign
def sign_key(dic):
    sign = hashlib.md5()
    s3 = '&'.join(sorted(['='.join([i, str(v)]) for i, v in dic.items() if v != ''])) + '&key=' + K
    sign.update(s3.encode('utf-8'))
    return sign.hexdigest().upper()


# # 京东的生成sign，测试
# def sign_key1(dic):
#     l = ['='.join([i, str(v)]) for i, v in dic.items() if v != '']
#     s2 = '&'.join(sorted(l))
#     sign = hashlib.md5()
#     s3 = s2 + '&key=' + K
#     sign.update(s3.encode('utf-8'))
#     return sign.hexdigest().upper()


# Turn a simple dict of key/value pairs into XML 生成xml数据
def dict_to_xml(tag, d):
    elem = Element(tag)
    for key, val in d.items():
        child = Element(key)
        child.text = str(val)
        elem.append(child)
    return elem


#生成随机字符串
def create_md5():    #通过MD5的方式创建
    m = hashlib.md5()
    m.update(bytes(str(time.time()),encoding='utf-8'))
    return m.hexdigest()[:30]


#生成订单号
def create_order(m_id):
    i = datetime.datetime.now()
    order_nmb = '8'+ m_id + i.strftime('%Y%m%d%H%M%S')
    return order_nmb


# 获取本机ip
def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


# 异步查询订单返回订单状态
def check_order(dic,order_for):

    #脚本测试设置下单后再调查询订单的时间，
    time.sleep(30)

    if order_for == 'wechat':
        check_url = KURL + '/wechat/orders/query'
    elif order_for == 'alipay':
        check_url = KURL + '/alipay/orders/query'
    elif order_for =='JDpay':
        check_url = KURL + '/jdpay/orders/query'

    check_dic = {}
    check_dic['mch_id'] = dic['mch_id']
    check_dic['out_trade_no'] = dic['out_trade_no']
    check_dic['nonce_str'] = create_md5()

    if order_for == 'JDpay':
        # 生成sign
        check_dic['sign'] = sign_key(check_dic)
    else:
        # 生成sign
        check_dic['sign'] = sign_key(check_dic)

    # 关闭请求参数转成字符串
    check_order1 = ' & '.join(['='.join([i, v]) for i, v in check_dic.items()])
    info_log.exception('请求url : {},查询了订单 : {},查询订单请求信息 : {}'.format(check_url,check_dic['out_trade_no'],check_order1))

    # 请求参数
    rs_xml = request_order(check_url, check_dic)

    # 从xml字符串中提取交易状态
    dom1 = minidom.parseString(rs_xml)
    return_code = dom1.getElementsByTagName("return_code")
    result_code = dom1.getElementsByTagName("result_code")

    return_code = return_code[0].childNodes[0].nodeValue
    result_code = result_code[0].childNodes[0].nodeValue

    #微信支付宝京东
    if return_code == 'SUCCESS' and result_code == 'SUCCESS':

        trade_state = dom1.getElementsByTagName("trade_state")
        trade_state = trade_state[0].childNodes[0].nodeValue

        if order_for == 'JDpay':
            pay_list = dom1.getElementsByTagName("pay_list")
            pay_list = pay_list[0].childNodes[0].nodeValue
            print('pay_list', pay_list)


        if trade_state == 'SUCCESS' or trade_state == 'TRADE_SUCCESS' or trade_state == '2':
            return rs_xml

        else:
            return trade_state



#成功支付存数据库
def insert_db(check_order_return,dic,channel,c_time):
    print('支付成功返回的结果',check_order_return)
    dom1 = minidom.parseString(check_order_return)
    trade_state = dom1.getElementsByTagName("trade_state")
    trade_type = dom1.getElementsByTagName("trade_type")
    out_trade_no = dom1.getElementsByTagName("out_trade_no")
    time_end = dom1.getElementsByTagName("time_end")
    total_fee = dom1.getElementsByTagName("total_fee")
    trade_state = trade_state[0].childNodes[0].nodeValue or None
    trade_type = trade_type[0].childNodes[0].nodeValue or None
    out_trade_no = out_trade_no[0].childNodes[0].nodeValue or None
    time_end = time_end[0].childNodes[0].nodeValue or None
    total_fee = total_fee[0].childNodes[0].nodeValue or None
    mch_id = dic['mch_id'] or None

    #支付时间格式转换
    time_end = time_end_type(time_end)
    print('存库数据',trade_state,trade_type,out_trade_no,total_fee,mch_id,c_time,time_end)

    new_order = mch_order(out_trade_no=out_trade_no, c_time=c_time,time_end=time_end, \
                         total_fee=int(total_fee), trade_type=trade_type, \
                         strade_state=trade_state, mch_id=mch_id,channel=channel)

    # 添加到session:
    session.add(new_order)
    # 提交即保存到数据库:
    session.commit()
    # 关闭session:
    session.close()


class Executor(ThreadPoolExecutor):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not getattr(cls, '_instance', None):
            cls._instance = ThreadPoolExecutor(max_workers=10)
        return cls._instance

#微信扫码支付
class WechatN(tornado.web.RequestHandler):

    executor = Executor()
    WechatN_url = KURL + '/wechat/orders'

    def get(self):
        self.render('wechatN.html')

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self,*args,**kwargs):
        dic = {}
        for key in self.request.arguments:
            dic[key] = self.get_arguments(key)[0]

        dic['nonce_str'] = create_md5()
        dic['spbill_create_ip'] = get_host_ip()
        dic['notify_url'] = '112233'
        dic['mch_id'] = MCH_ID
        dic['body'] = '奶粉钱'
        dic['out_trade_no'] = create_order(dic['mch_id'])
        dic['product_id'] = create_md5()
        dic['trade_type'] = 'NATIVE'

        # 生成sign
        dic['sign'] = sign_key(dic)
        # print(dic)

        # 请求参数返回数据
        rs_xml = request_order(WechatN.WechatN_url, dic)

        #下单请求参数转成字符串
        order = ' & '.join(['='.join([i, v]) for i, v in dic.items()])

        #从xml字符串中提取二维码
        dom1 = minidom.parseString(rs_xml)
        return_code = dom1.getElementsByTagName("return_code")
        result_code = dom1.getElementsByTagName("result_code")
        return_code = return_code[0].childNodes[0].nodeValue

        if result_code:
            result_code = result_code[0].childNodes[0].nodeValue


        if return_code == 'SUCCESS' and result_code == 'SUCCESS':
            #订单创建时间
            c_time = n_time() or None

            result = dom1.getElementsByTagName("code_url")
            result = result[0].childNodes[0].nodeValue

            out_trade_no = dom1.getElementsByTagName("out_trade_no")
            out_trade_no = out_trade_no[0].childNodes[0].nodeValue
            print('生成订单', out_trade_no)

            info_log.exception('请求url : {},创建了订单 : {},订单信息 : {}'.format(WechatN.WechatN_url,out_trade_no,order))

            self.render('weixin-code.html', result=result)

            order_for = 'wechat'

            # 异步查询订单返回订单状态
            future = Executor().submit(check_order,dic,order_for)
            check_order_return = yield tornado.gen.with_timeout(datetime.timedelta(30), future,
                                                      quiet_exceptions=tornado.gen.TimeoutError)

            print('返回的结果',check_order_return)
            if check_order_return == 'NOTPAY': # 没有支付，关闭订单
                close_url = KURL + '/wechat/orders/close'
                close_dic = {}
                close_dic['mch_id'] = dic['mch_id']
                close_dic['out_trade_no'] = dic['out_trade_no']
                close_dic['nonce_str'] = create_md5()
                # 生成sign
                close_dic['sign'] = sign_key(close_dic)

                # 关闭请求参数转成字符串
                close_order = ' & '.join(['='.join([i, v]) for i, v in close_dic.items()])

                # 请求参数返回数据
                rs_xml = request_order(close_url, close_dic)

                print('关闭订单', close_dic['out_trade_no'])
                info_log.exception('请求url : {},关闭了订单 : {},关闭订单请求信息 : {}'.format(close_url,close_dic['out_trade_no'],close_order))

            else:  #支付成功存数据库
                channel = 'wx'
                insert_db(check_order_return,dic,channel,c_time)

        else:
            # 请求下单错误
            return_msg = dom1.getElementsByTagName("err_code_des") or dom1.getElementsByTagName("return_msg")
            return_msg = return_msg[0].childNodes[0].nodeValue

            #日志
            error_log.exception('请求url : {} ,错误是 : {}，传入的参数是 : {}'.format(WechatN.WechatN_url,return_msg,order))

            self.write(return_msg)


#微信刷卡支付
class WechatP(tornado.web.RequestHandler):

    wechatP_url = KURL + '/wechat/orders/micropay'

    def get(self, *args, **kwargs):
        self.render('wechatP.html')

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        dic = {}
        for key in self.request.arguments:
            dic[key] = self.get_arguments(key)[0]

        dic['nonce_str'] = create_md5()
        dic['spbill_create_ip'] = get_host_ip()
        dic['mch_id'] = MCH_ID
        dic['detail'] = create_md5()
        dic['body'] = '奶粉钱'
        dic['out_trade_no'] = create_order(dic['mch_id'])

        # 生成sign
        dic['sign'] = sign_key(dic)

        # 请求参数返回数据
        rs_xml = request_order(WechatP.wechatP_url, dic)

        #从xml字符串中return_code
        dom1 = minidom.parseString(rs_xml)
        return_code = dom1.getElementsByTagName("return_code")
        return_code = return_code[0].childNodes[0].nodeValue

        if return_code == 'FAIL':
            return_msg = dom1.getElementsByTagName("return_msg")
            return_msg = return_msg[0].childNodes[0].nodeValue
            self.write(return_msg)


        else:
            self.finish(rs_xml)
            # 订单创建时间
            c_time = n_time() or None
            order_for = 'wechat'

            # 异步查询订单返回订单状态
            future = Executor().submit(check_order, dic, order_for)
            check_order_return = yield tornado.gen.with_timeout(datetime.timedelta(30), future,

                                                                quiet_exceptions=tornado.gen.TimeoutError)


            if check_order_return == None or check_order_return == 'USERPAYING' or check_order_return == 'PAYERROR' or check_order_return == 'NOTPAY':  # 没有支付，关闭订单
                close_url = KURL + '/wechat/orders/close'
                close_dic = {}
                close_dic['mch_id'] = dic['mch_id']
                close_dic['out_trade_no'] = dic['out_trade_no']
                close_dic['nonce_str'] = create_md5()
                # 生成sign
                close_dic['sign'] = sign_key(close_dic)

                # 关闭请求参数转成字符串
                close_order = ' & '.join(['='.join([i, v]) for i, v in close_dic.items()])

                # 请求参数返回数据
                rs_xml = request_order(close_url, close_dic)

                print('关闭订单', close_dic['out_trade_no'])
                info_log.exception(
                    '请求url : {},关闭了订单 : {},关闭订单请求信息 : {}'.format(close_url, close_dic['out_trade_no'], close_order))

            else:  # 支付成功存数据库
                channel = 'wx'
                insert_db(check_order_return, dic, channel, c_time)




#支付宝扫码支付
class AlipayN(tornado.web.RequestHandler):

    alipayN_url = KURL + '/alipay/orders/precreate'
    # alipayN_url = 'http://api.mch.spd.uline.cc/alipay/orders/precreate'


    def get(self, *args, **kwargs):
        self.render('alipayN.html')

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        dic = {}
        for key in self.request.arguments:
            dic[key] = self.get_arguments(key)[0]

        dic['nonce_str'] = create_md5()
        dic['spbill_create_ip'] = get_host_ip()
        dic['notify_url'] = 'http://alipayn.cn.com'
        dic['mch_id'] = MCH_ID
        dic['body'] = '1111'
        dic['out_trade_no'] = create_order(dic['mch_id'])
        dic['detail']= '备注信息'
        dic['timeout_express'] = '1m'
        dic['attach'] = '12345678'


        # 生成sign
        dic['sign'] = sign_key(dic)

        # 请求参数返回数据
        rs_xml = request_order(AlipayN.alipayN_url, dic)

        # 从xml字符串中提取二维码
        dom1 = minidom.parseString(rs_xml)

        return_code = dom1.getElementsByTagName("return_code")
        result_code = dom1.getElementsByTagName("result_code")

        if return_code and result_code:

            # 订单创建时间
            c_time = n_time() or None

            result = dom1.getElementsByTagName("qr_code")
            result = result[0].childNodes[0].nodeValue

            out_trade_no = dom1.getElementsByTagName("out_trade_no")
            out_trade_no = out_trade_no[0].childNodes[0].nodeValue
            print('生成订单', out_trade_no)

            self.render('weixin-code.html', result=result)


            order_for = 'alipay'

            future = Executor().submit(check_order, dic, order_for)
            check_order_return = yield tornado.gen.with_timeout(datetime.timedelta(30), future,
                                                                quiet_exceptions=tornado.gen.TimeoutError)

            if check_order_return:
                channel = 'alipay'
                insert_db(check_order_return, dic, channel,c_time)
            else:
                close_url = KURL + '/alipay/orders/close'
                close_dic = {}
                close_dic['mch_id'] = dic['mch_id']
                close_dic['out_trade_no'] = dic['out_trade_no']
                close_dic['nonce_str'] = create_md5()
                # 生成sign
                close_dic['sign'] = sign_key(close_dic)

                # 关闭请求参数转成字符串
                close_order = ' & '.join(['='.join([i, v]) for i, v in close_dic.items()])

                # 请求参数返回数据
                rs_xml = request_order(close_url, close_dic)

                print('关闭订单', close_dic['out_trade_no'])
                info_log.exception('请求url : {},关闭了订单 : {},关闭订单请求信息 : {}'.format(close_url,close_dic['out_trade_no'],close_order))


        else:
            return_msg = dom1.getElementsByTagName("return_msg")
            return_msg = return_msg[0].childNodes[0].nodeValue
            self.write(return_msg)


import pika
import uuid
class OrderonacciRpcClient(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        # 监听reply_to队列的结果
        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(  # 发送消息给服务器，并附带相关信息
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id
            ),
            body=n
        )
        while self.response is None:
            self.connection.process_data_events()
        return int(self.response)

# fibonacci_rpc = OrderonacciRpcClient()
# print("[x] Requestin fib(30)")
# response = fibonacci_rpc.call(30)
# print("[.].Got%r" % response)



# 支付宝扫码支付
class RabbitmqTestAlipayN(tornado.web.RequestHandler):

    alipayN_url = KURL + '/alipay/orders/precreate'

    # alipayN_url = 'http://api.mch.spd.uline.cc/alipay/orders/precreate'

    def prepare(self):
        self.orderonacci_rpc = OrderonacciRpcClient()


    def get(self, *args, **kwargs):
        self.render('rabbitmqtestalipayN.html')

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        dic = {}
        for key in self.request.arguments:
            dic[key] = self.get_arguments(key)[0]

        dic['nonce_str'] = create_md5()
        dic['spbill_create_ip'] = get_host_ip()
        dic['notify_url'] = 'http://alipayn.cn.com'
        dic['mch_id'] = MCH_ID
        dic['body'] = '1111'
        dic['out_trade_no'] = create_order(dic['mch_id'])

        # 生成sign
        dic['sign'] = sign_key(dic)

        # 请求参数返回数据
        rs_xml = request_order(AlipayN.alipayN_url, dic)

        # 从xml字符串中提取二维码
        dom1 = minidom.parseString(rs_xml)

        return_code = dom1.getElementsByTagName("return_code")
        result_code = dom1.getElementsByTagName("result_code")

        if return_code and result_code:

            # 订单创建时间
            c_time = n_time() or None

            result = dom1.getElementsByTagName("qr_code")
            result = result[0].childNodes[0].nodeValue

            out_trade_no = dom1.getElementsByTagName("out_trade_no")
            out_trade_no = out_trade_no[0].childNodes[0].nodeValue
            print('生成订单', out_trade_no)

            self.render('weixin-code.html', result=result)

            response = self.orderonacci_rpc.call(out_trade_no)
            print("[.].Got%r" % response)



        #     order_for = 'alipay'
        #
        #     future = Executor().submit(check_order, dic, order_for)
        #     check_order_return = yield tornado.gen.with_timeout(datetime.timedelta(30), future,
        #                                                         quiet_exceptions=tornado.gen.TimeoutError)
        #
        #     if check_order_return:
        #         channel = 'alipay'
        #         insert_db(check_order_return, dic, channel, c_time)
        #
        # else:
        #     return_msg = dom1.getElementsByTagName("return_msg")
        #     return_msg = return_msg[0].childNodes[0].nodeValue
        #     self.write(return_msg)



#支付宝刷卡支付
class AlipayP(tornado.web.RequestHandler):

    alipayP_url = KURL + '/alipay/orders/micropay'

    def get(self, *args, **kwargs):
        self.render('alipayP.html')

    def post(self, *args, **kwargs):
        dic = {}
        for key in self.request.arguments:
            dic[key] = self.get_arguments(key)[0]

        dic['nonce_str'] = create_md5()
        dic['spbill_create_ip'] = get_host_ip()
        dic['scene'] = 'bar_code'
        dic['notify_url'] = 'http://alipayp.cn.com'
        dic['mch_id'] = MCH_ID
        dic['body'] = '奶粉钱'
        dic['out_trade_no'] = create_order(dic['mch_id'])
        dic['timeout_express'] = '0.5m'

        # 生成sign
        dic['sign'] = sign_key(dic)

        # 请求参数返回数据
        rs_xml = request_order(AlipayP.alipayP_url, dic)

        dom1 = minidom.parseString(rs_xml)
        return_code = dom1.getElementsByTagName("return_code")
        return_code = return_code[0].childNodes[0].nodeValue

        transaction_id = dom1.getElementsByTagName("transaction_id")
        transaction_id = transaction_id[0].childNodes[0].nodeValue

        time.sleep(35)
        close_url = KURL + '/alipay/orders/query'
        close_dic = {}
        close_dic['mch_id'] = dic['mch_id']
        close_dic['transaction_id'] = transaction_id
        close_dic['nonce_str'] = create_md5()
        # 生成sign
        close_dic['sign'] = sign_key(close_dic)

        # 关闭请求参数转成字符串
        # close_order = ' & '.join(['='.join([i, v]) for i, v in close_dic.items()])

        # 请求参数返回数据
        rs_xml = request_order(close_url, close_dic)

        # if return_code == 'FAIL':
        #     return_msg = dom1.getElementsByTagName("return_msg")
        #     return_msg = return_msg[0].childNodes[0].nodeValue
        #     self.write(return_msg)
        #
        # else:
        #     time.sleep(1)
        #     close_url = KURL + '/alipay/orders/cancel'
        #     close_dic = {}
        #     close_dic['mch_id'] = dic['mch_id']
        #     close_dic['transaction_id'] = transaction_id
        #     close_dic['nonce_str'] = create_md5()
        #     # 生成sign
        #     close_dic['sign'] = sign_key(close_dic)
        #
        #     # 关闭请求参数转成字符串
        #     # close_order = ' & '.join(['='.join([i, v]) for i, v in close_dic.items()])
        #
        #     # 请求参数返回数据
        #     rs_xml = request_order(close_url, close_dic)


class WechatJS(tornado.web.RequestHandler):

    WechatJS_url = KURL + '/wechat/orders'

    def get(self, *args,**kwargs):
        self.render('wechatJS.html')

    def post(self, *args, **kwargs):
        dic = {}
        for key in self.request.arguments:
            dic[key] = self.get_arguments(key)[0]

        dic['nonce_str'] = create_md5()
        dic['spbill_create_ip'] = get_host_ip()
        dic['notify_url'] = 'http://wechatn.com.callback'
        dic['mch_id'] = MCH_ID
        dic['body'] = '奶粉钱'
        dic['out_trade_no'] = create_md5()
        dic['product_id'] = create_md5()
        dic['trade_type'] = 'JSAPI'

        # 生成sign
        dic['sign'] = sign_key(dic)
        # print(dic)

        # 数据转成xml格式
        xml_b = dict_to_xml('xml', dic)
        xml_str = tostring(xml_b).decode()

        # 请求
        r = requests.post(url=WechatJS.WechatJS_url, data=xml_str)
        rs_xml = r.content.decode()
        print(type(rs_xml), rs_xml)


    # WechatJS_url = 'http://api.mch.spd.uline.cc/wechat/orders'
    #
    # def get(self, *args, **kwargs):
    #     self.render('wechatJS.html')
    #
    # def post(self, *args, **kwargs):
    #     dic = {}
    #     for key in self.request.arguments:
    #         dic[key] = self.get_arguments(key)[0]
    #
    #     dic['nonce_str'] = create_md5()
    #     dic['spbill_create_ip'] = get_host_ip()
    #     dic['notify_url'] = 'http://wechatn.com.callback'
    #     dic['mch_id'] = '100042158132'
    #     dic['body'] = '奶粉钱'
    #     dic['out_trade_no'] = create_md5()
    #     dic['product_id'] = create_md5()
    #     dic['trade_type'] = 'MWEB'
    #     h5_dic = {'h5_info':{'type':'Wap','wap_url':'http://www.365worldshop.com/','wap_name':'新媒体O2O平台—智付通'}}
    #     dic['scene_info'] = h5_dic
    #
    #     # 生成sign
    #     dic['sign'] = sign_key(dic)
    #     print(2222222,dic)
    #
    #     # 数据转成xml格式
    #     xml_b = dict_to_xml('xml', dic)
    #     xml_str = tostring(xml_b).decode()
    #
    #     # 请求
    #     r = requests.post(url=WechatJS.WechatJS_url, data=xml_str)
    #     rs_xml = r.content.decode()
    #     print(type(rs_xml), rs_xml)


#商户交易
class AllOrder(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        orders = session.query(mch_order).order_by(-mch_order.id).all()

        #分页
        current_page = self.get_argument('p')
        if current_page.isdecimal():
            path = ''
            page_obj = Diy_page(len(orders),current_page, 5, 11,path)
            orders = orders[page_obj.start_page():page_obj.end_page()]
            if int(current_page) > page_obj.num_pages:
                self.write('请输入有效数字')
            else:
                self.render('allorder.html',orders=orders,page_obj=page_obj)
        else:
            self.write('请输入有效数字')



# 退款
class RefundOrder(tornado.web.RequestHandler):

    WX_refund_url = KURL + '/wechat/refunds'
    ALI_refund_url = KURL + '/alipay/refunds'

    def get(self, *args, **kwargs):
        out_trade_no = self.get_argument('out_trade_no')
        order = session.query(mch_order).filter(mch_order.out_trade_no == out_trade_no).one()
        self.render('refund.html',order=order)

    def post(self, *args, **kwargs):
        refund_dic = {}
        for key in self.request.arguments:
            refund_dic[key] = self.get_arguments(key)[0]

        refund_dic['nonce_str'] = create_md5()
        refund_dic['out_refund_no'] = create_md5()
        channel = refund_dic.pop('channel')

        print(channel)

        if channel == 'wx':  #微信退款
            rs_xml = self.refund_order(RefundOrder.WX_refund_url,refund_dic,refund_dic['out_trade_no'])

        else:    #支付宝退款
            refund_dic.pop('total_fee')
            rs_xml = self.refund_order(RefundOrder.ALI_refund_url, refund_dic,refund_dic['out_trade_no'])

        self.render('refund-back.html',rs_xml=rs_xml)


    def refund_order(self,url,dic,order):
        # 签名
        dic['sign'] = sign_key(dic)
        print('退款参数', dic)

        # 请求参数返回数据
        rs_xml = request_order(url, dic)

        # 从xml字符串中提取二维码
        dom1 = minidom.parseString(rs_xml)
        return_code = dom1.getElementsByTagName("return_code")
        return_code = return_code[0].childNodes[0].nodeValue

        if return_code == 'FAIL':
            return rs_xml
        else:
            result_code = dom1.getElementsByTagName("result_code")
            result_code = result_code[0].childNodes[0].nodeValue
            if return_code and result_code == 'SUCCESS':
                order = session.query(mch_order).filter(mch_order.out_trade_no == order).one()
                order.strade_state = '转入退款'

                # 添加到session:
                session.add(order)
                # 提交即保存到数据库:
                session.commit()
                # 关闭session:
                session.close()
            return rs_xml


class OrderDetail(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('Order_detail.html')


#对帐单测试
class Bills(tornado.web.RequestHandler):
    bills_url = KURL + '/bills'
    # bills_url = 'http://mapi.bosc.uline.cc/bills'
    def get(self, *args, **kwargs):
        self.render('bills.html')

    def post(self, *args, **kwargs):
        bills_dic = {}
        for key in self.request.arguments:
            bills_dic[key] = self.get_arguments(key)[0]

        bills_dic['nonce_str'] = create_md5()
        bills_dic['mch_id'] = MCH_ID

        # 生成sign
        bills_dic['sign'] = sign_key(bills_dic)

        # 请求参数返回数据
        rs_xml = request_order(Bills.bills_url, bills_dic)

        self.write(rs_xml)


#京东扫码支付
class JdPayN(tornado.web.RequestHandler):

    jdpay_url = KURL + '/jdpay/orders'

    def get(self, *args, **kwargs):
        self.render('jdpayN.html')

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        dic = {}
        for key in self.request.arguments:
            dic[key] = self.get_arguments(key)[0]

        dic['nonce_str'] = create_md5()
        dic['notify_url'] = 'http://alipayn.cn.com'
        dic['mch_id'] = MCH_ID
        dic['body'] = '奶粉钱'
        dic['out_trade_no'] = create_order(dic['mch_id'])
        dic['order_type'] = '0'
        dic['payment_code'] = 'JD_OFFLINE_NATIVE'

        # 生成sign
        dic['sign'] = sign_key(dic)

        # 请求参数返回数据
        rs_xml = request_order(JdPayN.jdpay_url, dic)

        # 从xml字符串中提取二维码
        dom1 = minidom.parseString(rs_xml)

        return_code = dom1.getElementsByTagName("return_code")
        result_code = dom1.getElementsByTagName("result_code")

        if return_code and result_code:
            # 订单创建时间
            c_time = n_time() or None

            result = dom1.getElementsByTagName("qr_code")
            result = result[0].childNodes[0].nodeValue

            out_trade_no = dom1.getElementsByTagName("out_trade_no")
            out_trade_no = out_trade_no[0].childNodes[0].nodeValue
            print('生成订单', out_trade_no)

            self.render('weixin-code.html', result=result)

            order_for = 'JDpay'

            future = Executor().submit(check_order, dic, order_for)
            check_order_return = yield tornado.gen.with_timeout(datetime.timedelta(30), future,
                                                                quiet_exceptions=tornado.gen.TimeoutError)


            if check_order_return != '2':
                print('没有支付',check_order_return)
            else:
                channel = 'JDpay'
                insert_db(check_order_return, dic, channel, c_time)

        else:
            return_msg = dom1.getElementsByTagName("return_msg")
            return_msg = return_msg[0].childNodes[0].nodeValue
            self.write(return_msg)


#京东二维码支付
class JdCodePay(tornado.web.RequestHandler):

    jdpay_url = KURL + '/jdpay/orders/customerpay'

    def get(self, *args, **kwargs):
        self.render('jdcodepay.html')

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        dic = {}
        for key in self.request.arguments:
            dic[key] = self.get_arguments(key)[0]

        dic['nonce_str'] = create_md5()
        dic['notify_url'] = 'http://alipayn.cn.com'
        dic['mch_id'] = MCH_ID
        dic['body'] = '奶粉钱'
        dic['out_trade_no'] = create_order(dic['mch_id'])
        dic['order_type'] = '0'
        dic['payment_code'] = 'JD_OFFLINE_JSAPI'
        dic['order_type'] = '0'
        dic['trade_type'] = 'DRCT'

        # 生成sign
        dic['sign'] = sign_key(dic)

        # 请求参数返回数据
        rs_xml = request_order(JdCodePay.jdpay_url, dic)

        print(rs_xml)
        # dom1 = minidom.parseString(rs_xml)
        # form = dom1.getElementsByTagName("form")
        # form = form[0].childNodes[0].nodeValue
        #
        # print(form)
        self.write(rs_xml)



class JdH5Pay(tornado.web.RequestHandler):
    jdpay_url = KURL + '/jdpay/orders/saveorder'

    def get(self, *args, **kwargs):
        self.render('jdh5pay.html')

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        dic = {}
        for key in self.request.arguments:
            dic[key] = self.get_arguments(key)[0]

        dic['nonce_str'] = create_md5()
        dic['notify_url'] = 'http://alipayn.cn.com'
        dic['mch_id'] = MCH_ID
        dic['body'] = '奶粉钱'
        dic['out_trade_no'] = create_order(dic['mch_id'])
        dic['order_type'] = '0'
        dic['payment_code'] = 'JD_ONLINE_H5_DEBIT'
        dic['user_id'] = '15920170132_p'
        dic['trade_type'] = 'PC'

        # 生成sign
        dic['sign'] = sign_key(dic)

        # 请求参数返回数据
        rs_xml = request_order(JdCodePay.jdpay_url, dic)

        dom1 = minidom.parseString(rs_xml)

        form = dom1.getElementsByTagName("form")
        form = form[0].childNodes[0].nodeValue
        import json
        dic_form = json.loads(form)

        for i,k in dic_form.items():
            print('{0} : {1}'.format(i,k))
        # import os
        #
        # tmp_path = os.getcwd()
        # tmp_path = tmp_path + '/tmplates/'
        # PC_JD = 'https://wepay.jd.com/jdpay/saveOrder'
        # req_JD = requests.post(url=PC_JD,data=dic_form)
        # f = open("%sdemo_1.html"% tmp_path, 'w')
        # f.write(req_JD.text)
        # f.close()
        #
        # self.render('demo_1.html')




class GetOpenid(tornado.web.RequestHandler):

    @coroutine
    def get(self, *args, **kwargs):
        get_openid_url = 'http://' + self.request.host + self.request.uri
        print(11111,get_openid_url)
        # mch_id = '111'
        code = self.get_query_argument('code', None)
        print(code)
        if None in [code]:
            self.write(u'无效请求')
            self.finish()
            return
        openid = yield self.get_openid(code)
        if not openid:
            self.redirect(
                'https://open.weixin.qq.com/connect/oauth2/authorize?appid={}&redirect_uri={}&response_type=code&scope=snsapi_base&state=STATE&connect_redirect=1#wechat_redirect'.format(
                    'wx2a4ff9f2959e2376', parse.quote(get_openid_url)))
            return
        # self.session['openid'] = openid
        # self.session.save()
        # xd = self.xsrf_token

        self.render('get-openid.html',get_openid_url=get_openid_url)


    @coroutine
    def get_openid(self, code):
        # 有可能会处理无效的code
        access_token = yield AsyncHTTPClient().fetch(
            "https://api.weixin.qq.com/sns/oauth2/access_token?appid={}&secret={}&code={}&grant_type=authorization_code".
                format('wx2a4ff9f2959e2376', 'bde23b1cff97eaeee12a489fa90b2a45', code), connect_timeout=5, request_timeout=5)

        body = access_token.body
        print(body)
        # body = json.loads(body)
        # raise Return(body.get('openid'))



from model.form import TestForm
class TestFormHandler(tornado.web.RequestHandler):

    def prepare(self):
        self.form = TestForm(self)

    def get(self):
        self.render('testform.html')

    def post(self):
        print(self.current_user)
        # print(self.request.arguments.keys())
        # print(self.form.data)
        self.form.img.raw_data = self.request.files.get(
            'img', None)

        if self.form.validate():
            print(self.form.img.raw_data[0].get('filename'))
            self.write('ok')
        else:
            self.write(self.form.errors)





class BaseHandler(tornado.web.RequestHandler):

    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)

    def get_current_user(self):
        return 'liaoboshi'

class TestHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.write(self.current_user)

    def post(self, *args, **kwargs):
        pass



from model.form import QueryForm
from sqlalchemy import or_
from sqlalchemy import and_
class TestQuery(tornado.web.RequestHandler):

    def prepare(self):
        self.form = QueryForm(self)
        self.current_page = self.get_argument('p',1)
        self.orders = self.db_execute(self.form)


    def get(self, *args, **kwargs):

        # orders = session.query(mch_order).order_by(-mch_order.id).all()
        # orders = self.db_execute(self.form)
        # 分页
        # current_page = self.get_argument('p')
        if self.current_page.isdecimal():
            path = ''
            page_obj = Diy_page(len(self.orders),  self.current_page, 5, 11, path)
            orders = self.orders[page_obj.start_page():page_obj.end_page()]
            if int( self.current_page) > page_obj.num_pages:
                self.write('请输入有效数字')
            else:
                self.render('testquery.html', orders=orders, page_obj=page_obj,form=self.form)
        else:
            self.write('请输入有效数字')


    def post(self, *args, **kwargs):
        # orders = self.db_execute(self.form)
        # 分页
        # current_page = self.get_argument('p')
        self.current_page = '1'
        if self.current_page.isdecimal():
            path = ''
            page_obj = Diy_page(len(self.orders),  self.current_page, 5, 11, path)
            orders = self.orders[page_obj.start_page():page_obj.end_page()]
            # print(current_page,page_obj.num_pages)
            if int( self.current_page) > page_obj.num_pages:
                self.write('请输入有效数字')
            else:
                self.render('testquery.html', orders=orders, page_obj=page_obj,form=self.form)
        else:
            self.write('请输入有效数字')

    def db_execute(self, form, offset=None):
        mch_id = form.mch_id.data or None
        channel = form.channel.data or None
        out_trade_no = form.out_trade_no.data or None

        print('mc',mch_id)
        print('ch',channel)
        print('ou',out_trade_no)

        if mch_id and channel and out_trade_no:
            orders = session.query(mch_order).filter\
                (and_(mch_order.mch_id == mch_id, mch_order.channel == channel,mch_order.out_trade_no == out_trade_no)).all()
        elif mch_id or channel or out_trade_no:
            orders = session.query(mch_order).filter\
                (or_(mch_order.mch_id == mch_id,mch_order.channel == channel,mch_order.out_trade_no == out_trade_no)).all()
        else:
            orders = session.query(mch_order).order_by(-mch_order.id).all()
        return orders

application = tornado.web.Application([

    (r"/", MainHandler),
    (r"/wechatJS$", WechatJS),
    (r"/wechat$", WechatN),
    (r"/wechatP$", WechatP),
    (r"/alipayN", AlipayN),
    (r"/rabbitmqtestalipayN",RabbitmqTestAlipayN),
    (r"/alipayP", AlipayP),
    (r"/allorder/",AllOrder),
    (r"/allorder/refund/",RefundOrder),
    (r"/allorder/order_detail$",OrderDetail),
    (r"/bills$",Bills),
    (r"/jdpayN",JdPayN),
    (r"/jdcodepay",JdCodePay),
    (r"/jdh5pay",JdH5Pay),
    (r"/getopenid",GetOpenid),
    (r'/testform',TestFormHandler),
    #测试get_current_user
    (r'/testhandler$',TestHandler),
    (r'/testquery/',TestQuery),



],**settings)


if __name__ == "__main__":
    application.listen(8021)
    tornado.ioloop.IOLoop.instance().start()



