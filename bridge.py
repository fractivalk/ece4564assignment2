#!/usr/bin/env python3

# file: rfcomm-server.py
# auth: Albert Huang <albert@csail.mit.edu>
# desc: simple demonstration of a server application that uses RFCOMM sockets
#
# $Id: rfcomm-server.py 518 2007-08-10 07:20:07Z albert $

import pymongo
from rmq_params import *
from bluetooth import *
import sys
import os

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

client_sock, client_info = server_sock.accept()
print("[Checkpoint 04] Accepted RFCOMM Bluetooth connection from ", client_info)

""" send rmq_params info to blueterm """

exchange = "Communicating on Exchange" + rmq_params['exchange'] + "\n"
client_sock.send(exchange)

client_sock.send("Available Queues: \n")

queue_set = rmq_params['queues']
for x in range(0, len(queue_set) - 1)
	client_sock.send(queue_set[x] + "\n")

try:
	buffer = ''
	while True:
		
		buffer += str(client_sock.recv(1024).decode("utf-8"))
		if '\r\n' in buffer: break #when the command has been entered fully, process
		
		"""
		data = str(input()) + '\r\n'
		client_sock.send(data)
		"""
	print("[Checkpoint 06] Received RFCOMM Bluetooth data: " + str(buffer))
		
except IOError:
	pass
	
except KeyboardInterrupt:
	print("disconnected")
	client_sock.close()
	server_sock.close()
	print("all done")