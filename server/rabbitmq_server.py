#!/usr/bin/env python
# -*- coding:utf8 -*-


#rabbitmq
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# make message persistent
channel.queue_declare(queue='rpc_queue', durable=True)  # 如果队列没有创建，就创建这个队列  durable：rabbitmq服务端宕机 消息不丢失


def fib(n):
    if n ==0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n-1) + fib(n-2)

def on_request(ch,method,props,body):  #获得了RPC的reply_to属性，处理完成后向这个队列发送消息
    n = int(body)

    print("[.]fib(%s)"%n)
    response = fib(n)

    ch.basic_publish(
        exchange='',
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=str(response)
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request,queue='rpc_queue')  #服务器监听队列消息

print("[x] Awaiting RPC request")
channel.start_consuming()

