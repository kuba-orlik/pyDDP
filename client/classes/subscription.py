import uuid
import api

def newSub(pub_name):
	req_body = {}
	req_body["verb"]="sub"
	req_body["attributes"]={}
	req_body["attributes"]["id"]=str(uuid.uuid4())
	req_body["attributes"]["pub_name"]=pub_name
	response = api.send_request(req_body)
	print(response)
	print(response["status"])

class Subscription():
	def __init__(self, pub_name):
		return
		