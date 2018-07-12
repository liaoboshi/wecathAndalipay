#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""
    支付宝支付相关配置以及PC端支付接口实现
"""

from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
from urllib.parse import quote_plus
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen
from base64 import decodebytes, encodebytes

import json


class AliPay(object):
    """
    支付宝支付接口
    """
    def __init__(
            self, appid,
            app_private_key_path,
            alipay_public_key_path,
            app_notify_url=None,
            return_url=None,
            debug=False
    ):
        self.appid = appid
        self.app_private_key_path = app_private_key_path
        self.alipay_public_key_path = alipay_public_key_path
        self.app_private_key = None
        self.alipay_public_key = None
        self.app_notify_url = app_notify_url
        self.return_url = return_url

        # 加载应用的私钥
        with open(self.app_private_key_path) as fp:
            self.app_private_key = RSA.importKey(fp.read())

        print(self.alipay_public_key_path)
        # 加载支付宝公钥
        with open(self.alipay_public_key_path) as fp:

            self.alipay_public_key = RSA.importKey(fp.read())

        if debug is True:
            self.__gateway = "https://openapi.alipaydev.com/gateway.do"
        else:
            self.__gateway = "https://openapi.alipay.com/gateway.do"

    def direct_pay(self, subject, out_trade_no, total_amount, **kwargs):
        biz_content = {
            "subject": subject,  # 标题
            "out_trade_no": out_trade_no,  # 订单号
            "total_amount": total_amount,  # 支付金额，单位元，精确到分
            "product_code": "FAST_INSTANT_TRADE_PAY",  # 销售产品码，目前仅支持这个类型
            # "qr_pay_mode":4
        }

        biz_content.update(kwargs)
        data = self.build_body("alipay.trade.page.pay", biz_content)
        return self.sign_data(data)

    def build_body(self, method, biz_content):
        data = {
            "app_id": self.appid,
            "method": method,
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }

        if self.return_url is not None:
            data["notify_url"] = self.app_notify_url
            data["return_url"] = self.return_url

        return data

    def sign_data(self, data):
        data.pop("sign", None)
        # 排序后[(k, v), ...]
        ordered_items = self.ordered_data(data)
        # 拼接成待签名的字符串
        unsigned_string = "&".join("{0}={1}".format(k, v) for k, v in ordered_items)
        # 对上一步得到的字符串进行签名
        sign = self.sign(unsigned_string.encode("utf-8"))
        # 处理URL
        quoted_string = "&".join("{0}={1}".format(k, quote_plus(v)) for k, v in ordered_items)
        # 添加签名，获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    def ordered_data(self, data):
        # 排序
        return sorted(((k, v if not isinstance(v, dict) else json.dumps(v, separators=(',', ':'))) for k, v in data.items()))

    def sign(self, unsigned_string):
        # 开始计算签名
        key = self.app_private_key
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(SHA256.new(unsigned_string))
        # base64 编码，转换为unicode表示并移除回车
        sign = encodebytes(signature).decode("utf8").replace("\n", "")
        return sign

    def _verify(self, raw_content, signature):
        """
        使用支付宝的公钥去加密原始数据，然后和签名值比较
        :param raw_content: 原始数据
        :param signature: 签名值
        :return:
        """
        key = self.alipay_public_key
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new()
        digest.update(raw_content.encode("utf8"))
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False

    def verify(self, data, signature):
        """
        验证
        :param data: 数据
        :param signature: 签名值
        :return:
        """
        if "sign_type" in data:
            sign_type = data.pop("sign_type")
        # 排序后的字符串
        ordered_items = self.ordered_data(data)
        message = "&".join(u"{}={}".format(k, v) for k, v in ordered_items)
        return self._verify(message, signature)

    def generate_payment_url(self, data):
        payment_url = self.__gateway + "?" + data
        return payment_url


if __name__ == "__main__":
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "luffy.settings")
    import django
    django.setup()
    from django.conf import settings
    return_url = "http://47.94.172.250:8804/api/v1/trade/alipay/?total_amount=487.00&timestamp=2017-09-20+14%3A26%3A30&sign=cLu4YN%2FLNFiEgSR%2BMG6kC7cCRnjPTpcrEcbsf5%2FByklQBhjV7vAadwZV2G1I51fAEbgk7JqHxXJ1raBbNwxbgh03Yjer7Wwim1joFu9xL276DYI3uwfOE2%2FFg74hPvqeRy6zXLdfAc7dIBwofJ1wxEeWN6QB1Mx7AiHuGA7JCZe8fcN1PZ4EPP54G4haGsav4mh7a3EI01Mx0VSiGFHClp%2BXdrcYbhzPOj8fVWKtOAxqtde7UIz%2B4867oSCnwamRodoyw5jdNQL9wNDjQLkwbr8lbjzAhzmENCw%2Fj2nvDweCLzZmcR%2BTr7YxoeA6ucok4hRWDLWin2Ge0%2Fj1EHbcLA%3D%3D&trade_no=2017092021001004590200327653&sign_type=RSA2&auth_app_id=2016081500252288&charset=utf-8&seller_id=2088102171291279&method=alipay.trade.page.pay.return&app_id=2016081500252288&out_trade_no=20170920142517169&version=1.0"
    # 生成支付实例
    alipay = AliPay(
        appid=settings.ALIPAY_CONFIG["app_id"],
        app_notify_url=None,
        app_private_key_path=settings.ALIPAY_CONFIG["app_private_key_path"],
        alipay_public_key_path=settings.ALIPAY_CONFIG["alipay_public_key_path"],  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        debug=True,  # 默认False,
    )

    # 以下为验证return_url中的sign 可以先不看

    o = urlparse(return_url)
    query = parse_qs(o.query)
    processed_query = {}
    ali_sign = query.pop("sign")[0]
    for key, value in query.items():
        processed_query[key] = value[0]

    print(alipay.verify(processed_query, ali_sign))
    # 可以先不看

    # 创建URL
    data = alipay.direct_pay(
        subject="tiaoshimoshi",
        out_trade_no="201709191448908",
        total_amount=999.00
    )
    # 拼接最终的URL
    re_url = alipay.generate_payment_url(data)
    print(re_url)