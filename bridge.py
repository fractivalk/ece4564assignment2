#!/usr/bin/env python3

# file: rfcomm-server.py
# auth: Albert Huang <albert@csail.mit.edu>
# desc: simple demonstration of a server application that uses RFCOMM sockets
#
# $Id: rfcomm-server.py 518 2007-08-10 07:20:07Z albert $

import pymongo
import time
import re
from rmq_params import *
from bluetooth import *
import sys
import os
import pika
import pprint

def callback(ch, method, properties, body):
	print("%r:%r" % (method.routing_key, body))

if len(sys.argv) != 3 or sys.argv[1] != '-s':
    print('Invalid arguments')
    sys.exit(0)

db = pymongo.MongoClient()[rmq_params['exchange']]
for item in list(rmq_params['queues']):
	db[item].drop()

print("[Checkpoint 01] Connected to database {} on MongoDB server at 'localhost'".format(rmq_params['exchange']))

credentials = pika.PlainCredentials(rmq_params['username'], rmq_params['password'])
parameters = pika.ConnectionParameters(sys.argv[2], virtual_host=rmq_params['vhost'], credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
print("[Checkpoint 02] Connected to vhost '{}' on RMQ server at '{}' as user '{}'".format(rmq_params['vhost'], sys.argv[2], rmq_params['username']))

channel.exchange_declare(exchange=rmq_params['exchange'], exchange_type='direct')

server_sock=BluetoothSocket( RFCOMM )
server_sock.bind(("",PORT_ANY))
server_sock.listen(1)


port = server_sock.getsockname()[1]

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

advertise_service( server_sock, "BTServer",
				   service_id = uuid,
				   service_classes = [ uuid, SERIAL_PORT_CLASS ],
				   profiles = [ SERIAL_PORT_PROFILE ], 
					)
				   
print("[Checkpoint 03] Created RFCOMM Bluetooth socket on port 1")

while True:
	client_sock, client_info = server_sock.accept()
	print("[Checkpoint 04] Accepted RFCOMM Bluetooth connection from ", client_info)
	channel.basic_publish(exchange=rmq_params['exchange'], routing_key = rmq_params['status_queue'], body = 'green')
	print("[Checkpoint p-01] Published message with routing_key: 'ex_status'")
	print("[Checkpoint p-02] Message: green")


	""" send rmq_params info to blueterm """
	print("[Checkpoint 05] Sending Exchange and Queue names")
	exchange = "Communicating on Exchange: " + rmq_params['exchange'] + '\r\n'
	client_sock.send(exchange)

	client_sock.send("Available Queues: \r\n")

	queue_set = rmq_params['queues']
	for i in queue_set:
		temp = str(i + "\r\n")
		client_sock.send(temp)

	try:
		buffer = ''
		btCommand = ''
		while True:
			buffer += str(client_sock.recv(1024).decode("utf-8"))
			if '\r\n' in buffer: 
				buffer = buffer[:-2]
				print("[Checkpoint 06] Received RFCOMM Bluetooth data: " + str(buffer))
				btCommand = str(buffer)
				buffer = '' #when the command has been entered fully, process
			
			if btCommand[:1] == 'p':
				prodMatch = re.match('p:(\w+) "([\w+\s+]+)"', btCommand)
				if prodMatch.group(1) not in list(rmq_params['queues']):
					print("invalid input")
					client_sock.send("invalid input")
					continue
				if not prodMatch:
					print("invalid input")
					continue
				print("[Checkpoint p-01] Published message with routing_key: " + rmq_params['status_queue'])
				print("[Checkpoint p-02] Message: purple")
				print("[Checkpoint p-01] Published message with routing_key: " + prodMatch.group(1))
				print("[Checkpoint p-02] Message: " + prodMatch.group(2))
				channel.basic_publish(exchange=rmq_params['exchange'], routing_key = rmq_params['status_queue'], body = 'purple')
				channel.basic_publish(exchange=rmq_params['exchange'], routing_key = prodMatch.group(1), body = prodMatch.group(2))
				btCommand = ''
				doc = {"Subject": prodMatch.group(1), "Action": "p", "MsgID": "team_10$" + str(time.time()), "Place": rmq_params['exchange'], "Message": prodMatch.group(2)}
				db[prodMatch.group(1)].insert_one(doc)
				print("[Checkpoint m-01] Stored document in collection '{}' in MongoDB database '{}'".format(prodMatch.group(1), rmq_params['exchange']))
				print("[Checkpoint m-02] Document: " + str(doc))

			elif btCommand[:1] == 'c':
				conMatch = re.match('c:(\w+)', btCommand)
				if conMatch.group(1) not in list(rmq_params['queues']):
					print("invalid input")
					client_sock.send("invalid input")
					continue
				if not conMatch:
					print("invalid input")
					continue
				print("[Checkpoint p-01] Published message with routing_key: " + rmq_params['status_queue'])
				print("[Checkpoint p-02] Message: yellow")
				channel.basic_publish(exchange=rmq_params['exchange'], routing_key = rmq_params['status_queue'], body = 'yellow')
				(method, properties, body) = channel.basic_get(queue=conMatch.group(1), no_ack=True)
				print("[Checkpoint c-01] Consumed a message published with routing_key:" + method.routing_key)
				print("[Checkpoint c-02] Message: " + str(body))
				print("[Checkpoint c-03] Sending to RFCOMM Bluetooth client")
				client_sock.send(str(body) + '\r\n')
				doc2 = {"Subject": conMatch.group(1), "Action": "c", "MsgID": "team_10$" + str(time.time()), "Place": rmq_params['exchange'], "Message": ""}
				db[conMatch.group(1)].insert_one(doc2)
				print("[Checkpoint m-01] Stored document in collection '{}' in MongoDB database '{}'".format(conMatch.group(1), rmq_params['exchange']))
				print("[Checkpoint m-02] Document: " + str(doc2))
				btCommand = ''

			elif btCommand[:1] == 'h':
				conMatch = re.match('h:(\w+)', btCommand)
				if conMatch.group(1) not in list(rmq_params['queues']):
					print("invalid input")
					client_sock.send("invalid input")
					continue
				if not conMatch:
					print("invalid input")
					continue
				print("[Checkpoint p-01] Published message with routing_key: " + rmq_params['status_queue'])
				print("[Checkpoint p-02] Message: blue")
				channel.basic_publish(exchange=rmq_params['exchange'], routing_key = rmq_params['status_queue'], body = 'blue')
				print("[Checkpoint h-01] Printing history of Collection '" + conMatch.group(1) + "' in MongoDB database " + rmq_params['exchange'])
				print("[Checkpoint h-02] Collection: " + conMatch.group(1))
				counter = 0;
				for item in db[conMatch.group(1)].find():
					print("Document {}: {}".format(counter, str(item)))
					counter += 1
				btCommand = ''

			
	except IOError:
		channel.basic_publish(exchange=rmq_params['exchange'], routing_key = rmq_params['status_queue'], body = 'red')
		print("[Checkpoint 07] RFCOMM Bluetooth client disconnected")
		print("[Checkpoint p-01] Published message with routing_key: " + rmq_params['status_queue'])
		print("[Checkpoint p-02] Message: red")
		pass
		
	except KeyboardInterrupt:
		print("disconnected")
		client_sock.close()
		server_sock.close()
		print("all done")