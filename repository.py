import pika 
import sys
from rmq_params import *

credentials = pika.PlainCredentials(rmq_params['username'], rmq_params['password'])
parameters = pika.ConnectionParameters(host=sys.argv[2], virtual_host=rmq_params['vhost'], credentials=credentials)
connection = pika.BlockingConnection(parameters)

channel = connection.channel()
channel.exchange_declare(exchange=rmq_params['exchange'], exchange_type='direct')

channel.queue_declare(queue='fuck')
print("adsf")

for item in list(rmq_params['queues']):
    channel.queue_declare(queue=item)
    print('sdf')
channel.queue_declare(queue=rmq_params['master_queue'])
channel.queue_declare(queue=rmq_params['status_queue'])

print('here')
    

