import json
import jsonpatch
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

def update(name, patch_to_apply):
	req_body = {}
	req_body["verb"]="update_pub"
	req_body["attributes"]={}
	req_body["attributes"]["pub_name"]=name
	try:
		patch_to_apply = json.loads(patch_to_apply)
	except:
		return -3
	req_body["attributes"]["changes"]=patch_to_apply
	response = api.send_request(req_body)
	res_number = response["res_number"]
	if res_number==300:
		#invalid patch:
		return -1
	elif res_number==404:
		return -2
	elif res_number==200:
		return 0
	else:
		return -100

def replace(name, new_content_str):
	try:
		new_content = json.loads(new_content_str)
	except:
		return -3
	req_body = {}
	req_body["verb"]="replace_pub"
	req_body["attributes"]={}
	req_body["attributes"]["pub_name"]=name
	req_body["attributes"]["new_content"]=new_content
	response = api.send_request(req_body)
	res_number = response["res_number"]
	#print(response)
	if res_number==404:
		return -1
	elif res_number==200:
		return 0
	else:
		return -100

def delete(name):
	req_body = {}
	req_body["verb"]="delete_pub"
	req_body["attributes"]={}
	req_body["attributes"]["name"]=name
	response = api.send_request(req_body)
	code = response["res_number"]
	if code==404:
		return -1
	elif code==200:
		return 0
	else:
		return -100