#!/usr/bin/env python
# coding=utf-8
import os
import logging
import pika
import subprocess

#before anything we need to aks things
machine_name = raw_input("Enter machine name: ")

internal_password = os.urandom(45).encode('base64')
external_password = os.urandom(45).encode('base64')

#defining queue
queueClient = "katzenhuter_" + machine_name + "_client"
queueServer = "katzenhuter_" + machine_name + "_server"

#defining logging
logging.basicConfig()

#connection
rabbit_connectionParameters = pika.ConnectionParameters(
    host="turtle.rmq.cloudamqp.com",
    port=5672,
    virtual_host="egresuqf",
    credentials=pika.PlainCredentials("egresuqf", "N7pA4GZsEln_wd8kTGyQVMPRBQjC1uvc")
)
rabbit_connection = pika.BlockingConnection(rabbit_connectionParameters)

rabbit_chanel = rabbit_connection.channel()
rabbit_chanel.queue_declare(queue=queueClient, durable=True)
rabbit_chanel.queue_declare(queue=queueServer, durable=True)

print("Katzenhuter watching \n" +
      "machine name: " + machine_name + "\n"
                                        "internal password: " + internal_password +
      "external password: " + external_password)


def send_to_monitor(message):
    print(message)
    rabbit_chanel.basic_publish(
        exchange='',
        routing_key=queueServer,
        body=message
    )


def get_orders_from_monitor(chanel, method, properties, body):
    print("[x] Received %r" % (body,))
    process = subprocess.Popen(body, stdout=subprocess.PIPE, stderr=None, shell=True)
    output = process.communicate()
    send_to_monitor(body + output[0])


rabbit_chanel.basic_consume(
    get_orders_from_monitor,
    queue=queueClient,
    no_ack=True
)

rabbit_chanel.start_consuming()