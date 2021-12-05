
import pickle
import platform
import io
import os
import sys
import pika
import redis
import hashlib
import json
import requests

from scrape import *
from db import *


hostname = platform.node()


## Configure test vs. production
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"
print(f"Connecting to rabbitmq({rabbitMQHost})")
                                                           

## Set up rabbitmq connection
rabbitMQ = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitMQHost))
rabbitMQChannel = rabbitMQ.channel()
toWorkerResult = rabbitMQChannel.queue_declare(queue='toWorker')

queue_name = toWorkerResult.method.queue


def enqueueDataToLogsExchange(message,messageType):
    rabbitMQ = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitMQHost))
    rabbitMQChannel = rabbitMQ.channel()

    rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')

    infoKey = f"{platform.node()}.worker.info"
    debugKey = f"{platform.node()}.worker.debug"

    if messageType == "info":
        key = infoKey
    elif messageType == "debug":
        key = debugKey

    rabbitMQChannel.basic_publish(
        exchange='logs', routing_key='logs', body=json.dumps(message))

    print(" [x] Sent %r:%r" % (key, message))

    rabbitMQChannel.close()
    rabbitMQ.close()



def callback(ch, method, properties, body):
    print(f" [x] {method.routing_key}:{body}", file=sys.stdout, flush=True)
    queuedata = json.loads(body)

    link = body['link']

    execute_scraper(link)

    sys.stdout.flush()
    sys.stderr.flush()


rabbitMQChannel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

rabbitMQChannel.start_consuming()