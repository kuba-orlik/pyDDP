import json
import api

def create(name, body_str):
	req_body = {}
	req_body["verb"]="new_pub"
	req_body["attributes"]={}
	req_body["attributes"]["name"]=name
	try:
		body_obj = json.loads(body_str)
	except:
		return -1
	req_body["attributes"]["content"]=body_obj
	response = api.send_request(req_body)
	if response["res_number"]==420:
		return -2
	else:
		return 0