import uuid
import api

def newSub(pub_name):
	req_body = {}
	req_body["verb"]="sub"
	req_body["attributes"]={}
	new_sub_id = str(uuid.uuid4())
	req_body["attributes"]["id"]=new_sub_id
	req_body["attributes"]["pub_name"]=pub_name
	response = api.send_request(req_body)
	if response["status"]=="ok":
		sub = Subscription(pub_name, response["message"], new_sub_id)
		return sub
	else:
		raise Exception("publication does not exist")
	#print(response["status"])

collection = []

def unsub(sub_index):
	current_sub = collection[sub_index]
	req_body={}
	req_body["verb"]="unsub"
	req_body["attributes"]={}
	req_body["attributes"]["sub_id"]=current_sub.id

	collection.remove(current_sub)

	print("\nsucessfully unsubscribed\n\n")

class Subscription():
	def __init__(self, pub_name, content, idL):
		global collection
		collection.append(self)
		self.pub_name = pub_name
		self.pub_content = content
		self.id=idL
		return
		