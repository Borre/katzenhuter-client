#!/usr/bin/env python
# coding=utf-8
import os
import logging
import pika
import json
import subprocess

#before anything we need to aks things
machine_name = "test"

internal_password = os.urandom(45).encode('base64').strip()
external_password = os.urandom(45).encode('base64').strip()

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
                                        "internal password: " + internal_password + "\n" +
      "external password: " + external_password)


def send_to_monitor(message):
    rabbit_chanel.basic_publish(
        exchange='',
        routing_key=queueServer,
        body=message
    )


def get_orders_from_monitor(chanel, method, properties, body):
    message = json.loads(body)
    password = message["password"].strip()
    command = message["message"].strip()
    if password == internal_password:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
        output = process.communicate()
        send_to_monitor(output[0])
    else:
        returned_message = '{"password": "' + external_password + '", "message": "bad password"}'.strip()
        send_to_monitor(returned_message)


rabbit_chanel.basic_consume(
    get_orders_from_monitor,
    queue=queueClient,
    no_ack=True
)

rabbit_chanel.start_consuming()