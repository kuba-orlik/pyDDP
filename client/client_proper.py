import socket
import select
import threading
import sys
import queue

from sys import path
path.append("classes/")

import api

HOST = 'localhost'   
PORT = 50007         
main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#main_socket.setblocking(0)
try:
	main_socket.connect((HOST, PORT))
except ConnectionRefusedError:
	print("Could not connect to the server. Is it turned on?")

api.use_socket(main_socket)

def listening_loop():
	while 1:
	#	if not api.requests_to_send.empty():
		send = True
		try:
			req = api.requests_to_send.get(False)
		except queue.Empty:
			send=False
			print("queue empty")
		if send:
			print("request queue not empty")
			req_body_str = req.getBodyString()
			main_socket.send(bytes(req_body_str, "UTF-8"))
			api.sent_requests.append(req)
		#handle the info
		ready = select.select([main_socket], [], [], 0.5)
		if ready[0]:
			data = main_socket.recv(2048)
			data = str(data, encoding='UTF-8')
			api.handle_server_response(repr(data))
			#print('Received', repr(data))

listening_thread = threading.Thread(target=listening_loop, args=() )
listening_thread.start()

to_send = {"verb":"delete_pub", "attributes":{"name":"test234"}}
print("about to send request")
response = api.send_request(to_send)

print("main", response)
