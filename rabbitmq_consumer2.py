#!/usr/bin/env python
# -*- coding:utf8 -*-

import pika
# ########################### 消费者 ###########################

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# make message persistent
channel.queue_declare(queue='hello', durable=True)  # 如果队列没有创建，就创建这个队列  durable：rabbitmq服务端宕机 消息不丢失


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    import time
    time.sleep(10)
    print('ok')
    ch.basic_ack(delivery_tag = method.delivery_tag)   #消息不丢失的关键代码：

channel.basic_consume(callback,
                      queue='hello',   # 队列名
                      no_ack=False)  # no-ack＝False：rabbitmq消费者连接断了 消息不丢失

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()