import request
import time
import json
import queue
global main_socket
global requests_to_send		

requests_to_send=queue.Queue()

sent_requests = []

answered = []

def use_socket(socket):
	global main_socket
	main_socket = socket

def send_request(req_body):
	global requests_to_send
	req = request.Request(req_body)
	requests_to_send.put(req)
	while req.waiting:
		time.sleep(0.1)
	#print("about to return from send_request")
	return req.response_obj

def getSentRequestByID(req_id):
	global sent_requests
	for req in sent_requests:
		#print(str(req.id), req_id)
		if str(req.id)==req_id:
			#print("found!")
			return req
	return None

def handle_server_response(response):
	global sent_request
	if response[0]=="'":
		response = response[1:len(response)-1]
	print(response)
	response_body = json.loads(response)
	req_id=response_body["request_id"]
	req_obj = getSentRequestByID(req_id)
	if not req_obj==None:
		req_obj.setServerResponse(response_body)
		sent_requests.remove(req_obj)