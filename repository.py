import pika 
import sys
from rmq_params import *

credentials = pika.PlainCredentials(rmq_params['username'], rmq_params['password'])
parameters = pika.ConnectionParameters(host='localhost', virtual_host=rmq_params['vhost'], credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

print("[Checkpoint 01] Connected to vhost '{}' on RMQ server at 'localhost' as user '{}'".format(rmq_params['vhost'], rmq_params['username']))

channel.exchange_declare(exchange=rmq_params['exchange'], exchange_type='direct')
channel.queue_declare(queue=rmq_params['master_queue'])
channel.queue_declare(queue=rmq_params['status_queue'])
channel.queue_purge(queue=rmq_params['master_queue'])
channel.queue_purge(queue=rmq_params['status_queue'])
channel.queue_bind(exchange=rmq_params['exchange'], 
                    queue=rmq_params['status_queue'], 
                    routing_key=rmq_params['status_queue'])


for item in list(rmq_params['queues']):
    channel.queue_declare(queue=item)
    channel.queue_purge(queue=item)
    channel.queue_bind(exchange=rmq_params['exchange'], queue=item, routing_key=item)
    channel.queue_bind(exchange=rmq_params['exchange'], queue=rmq_params['master_queue'], routing_key=item)

def master_callback(ch, method, properties, body):
    print("[Checkpoint 03] Consumed a message published with routing_key: '{}'".format(method.routing_key))
    print("[Checkpoint 04] Message: {}".format(body))
    
def status_callback(ch, method, properties, body):
    print("[Checkpoint l-01] Flashing LED to {}".format(body))
 
channel.basic_consume(master_callback, queue=rmq_params['master_queue'], no_ack=True)
channel.basic_consume(status_callback, queue=rmq_params['status_queue'], no_ack=True)

channel.start_consuming()

