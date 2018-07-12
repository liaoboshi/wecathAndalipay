#!/usr/bin/env python
# -*- coding:utf8 -*-


import pika
# ############################## 生产者 ##############################

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# make message persistent
channel.queue_declare(queue='hello', durable=True)  # 如果队列没有创建，就创建这个队列

channel.basic_publish(exchange='',
                      routing_key='hello',  # 指定队列的关键字为，这里是队列的名字
                      body='Hello World!1111',   # 往队列里发的消息内容
                      properties=pika.BasicProperties(
                          delivery_mode=2, # make message persistent
                      ))
print(" [x] Sent 'Hello World!'")
connection.close()