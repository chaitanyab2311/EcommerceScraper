##
from flask import Flask, request, Response, jsonify
import platform
import io, os, sys
import pika, redis
import hashlib, requests
import json
import pickle
import platform

from scrape import *
from db import *

from flask_cors import CORS
app = Flask(__name__)




# Initialize the Flask application
app = Flask(__name__)
CORS(app) # This will enable CORS for all routes


##
## Configure test vs. production
##
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

print("Connecting to rabbitmq({})".format(rabbitMQHost))



def enqueueDataToLogsExchange(message,messageType):
    rabbitMQ = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitMQHost))
    rabbitMQChannel = rabbitMQ.channel()

    rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')

    infoKey = f"{platform.node()}.rest.info"
    debugKey = f"{platform.node()}.rest.debug"

    if messageType == "info":
        key = infoKey
    elif messageType == "debug":
        key = debugKey

    rabbitMQChannel.basic_publish(
        exchange='logs', routing_key='logs', body=json.dumps(message))

    print(" [x] Sent %r:%r" % (key, message))

    rabbitMQChannel.close()
    rabbitMQ.close()


def enqueueDataToWorker(message):
    rabbitMQ = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitMQHost))
    rabbitMQChannel = rabbitMQ.channel()

    rabbitMQChannel.queue_declare(queue='toWorker')

    rabbitMQChannel.basic_publish(
        exchange='', routing_key='toWorker',
        properties=pika.BasicProperties(correlation_id = props.correlation_id),
        body=json.dumps(message))
    
    ch.basic_ack(delivery_tag=method.delivery_tag)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

    print(" [x] Sent %r:%r" % ('toWorker', message))

    rabbitMQChannel.close()
    rabbitMQ.close()


@app.route('/apiv1/fetchPrices', methods=['POST'])
def analyze():
    try:

        # enqueueDataToLogsExchange('Into fetch prices api',"info")

        data = request.get_json()
        print("-------Data-------" + str(data))
        product = data['product_name']
        final_output = start_scraping(product)
        response = insert_prices(final_output)
        addSearchProduct(product)



        # response = {
        #     "amazon" :[
        #         {
        #             "product_name":"iphone X",
        #             "product_price" : 230
        #         },
        #         {
        #             "product_name":"iphone X",
        #             "product_price" : 270
        #         }
        #     ],
        #     "ebay":[
        #         {
        #              "product_name":"iphone X",
        #             "product_price" : 130
        #         },
        #         {
        #             "product_name":"iphone X",
        #             "product_price" : 430
        #         }
        #     ]
        # }

        # enqueueDataToLogsExchange('Fetch prices api executed succesfully',"info")

        return Response(response=json.dumps(response), status=200, mimetype="application/json")
        
    except Exception as e:
        enqueueDataToLogsExchange('Error occured in api /apiv1/analyze','info')
        return Response(response="Something went wrong!", status=500, mimetype="application/json")


@app.route('/apiv1/getMostSearched', methods=['POST'])
def most_searched():
    try:
        most_searched = getMostSearchedProducts()
        print(most_searched)
        return Response(response=json.dumps(most_searched), status=200, mimetype="application/json")

    except Exception as e:
        enqueueDataToLogsExchange('Error occured in api /apiv1/analyze','info')
        return Response(response="Something went wrong!", status=500, mimetype="application/json")



# start flask app
app.run(host="0.0.0.0", port=5000)
